"""LangGraph workflow orchestration for Risk Intelligence Agent.

This module defines the state graph that orchestrates all components into
a single auditable pipeline.

**Validates Requirements**: 8.1-8.9, 14.1-14.8
"""

from typing import TypedDict, Optional, List, Any, Annotated
from datetime import datetime
import uuid
import numpy as np
import operator

from langgraph.graph import StateGraph, END

from .schemas import (
    MSMEInput, ValidatedData, FeatureVector, PolicyReport, FraudReport,
    RiskPrediction, SHAPExplanation, GeminiReasoning, FinancialHealthScore,
    ConfidenceBreakdown, AssessmentReport, AuditEntry
)
from .validator import validate
from .feature_engineering import engineer_features
from .policy_engine import evaluate_policy
from .fraud_engine import detect_fraud
from .xgboost_model import load_model
from .shap_explainer import explain
from .gemini_reasoner import reason
from .financial_health import compute_financial_health_score
from .confidence import compute_confidence


# ============================================================================
# State Definition
# ============================================================================

class AgentState(TypedDict):
    """State passed between workflow nodes."""
    # Input
    input: MSMEInput
    request_id: str
    
    # Intermediate outputs
    validated_data: Optional[ValidatedData]
    feature_vector: Optional[FeatureVector]
    policy_report: Optional[PolicyReport]
    fraud_report: Optional[FraudReport]
    risk_prediction: Optional[RiskPrediction]
    shap_explanation: Optional[SHAPExplanation]
    gemini_reasoning: Optional[GeminiReasoning]
    financial_health_score: Optional[FinancialHealthScore]
    confidence_breakdown: Optional[ConfidenceBreakdown]
    
    # Output
    final_report: Optional[AssessmentReport]
    
    # Error tracking
    errors: Annotated[List[dict], operator.add]
    audit_trail: Annotated[List[AuditEntry], operator.add]
    
    # Shared resources
    model: Optional[Any]
    all_registered_accounts: set


# ============================================================================
# Workflow Nodes
# ============================================================================

async def validate_data_node(state: AgentState) -> dict:
    """Node 1: Validate input data."""
    start_time = datetime.now()
    validated_data = None
    errors = []
    audit_trail = []
    
    try:
        # Convert Pydantic model to dictionary
        input_data = state['input']
        if hasattr(input_data, 'model_dump'):
            input_dict = input_data.model_dump()
        elif hasattr(input_data, 'dict'):
            input_dict = input_data.dict()
        else:
            input_dict = input_data
            
        # Validate input
        result = validate(input_dict)
        
        # Check if validation succeeded
        if hasattr(result, 'status') and result.status == "VALIDATED":
            validated_data = result
            
            # Log audit entry
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            audit_trail.append(AuditEntry(
                component="validate_data",
                timestamp=datetime.now(),
                duration_ms=duration_ms,
                input_summary={"gstin": state['input'].gstin},
                output_summary={"status": "VALIDATED", "sources": result.data_sources_available}
            ))
        else:
            # Validation failed
            errors.append({
                "component": "validate_data",
                "error": "Validation failed",
                "details": result
            })
            
    except Exception as e:
        errors.append({
            "component": "validate_data",
            "error": str(e)
        })
    
    return {
        "validated_data": validated_data,
        "errors": errors,
        "audit_trail": audit_trail
    }


async def engineer_features_node(state: AgentState) -> dict:
    """Node 2: Engineer features from validated data."""
    start_time = datetime.now()
    feature_vector = None
    errors = []
    audit_trail = []
    
    try:
        if state['validated_data'] is None:
            raise ValueError("No validated data available")
        
        # Engineer features
        feature_vector = engineer_features(state['validated_data'])
        
        # Log audit entry
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        audit_trail.append(AuditEntry(
            component="engineer_features",
            timestamp=datetime.now(),
            duration_ms=duration_ms,
            input_summary={"gstin": state['input'].gstin},
            output_summary={"num_features": len(feature_vector.values), "null_count": sum(feature_vector.null_flags)}
        ))
        
    except Exception as e:
        errors.append({
            "component": "engineer_features",
            "error": str(e)
        })
    
    return {
        "feature_vector": feature_vector,
        "errors": errors,
        "audit_trail": audit_trail
    }


async def policy_engine_node(state: AgentState) -> dict:
    """Node 3a: Evaluate policy rules (runs in parallel with fraud_engine)."""
    start_time = datetime.now()
    policy_report = None
    errors = []
    audit_trail = []
    
    try:
        if state['feature_vector'] is None or state['validated_data'] is None:
            raise ValueError("Missing feature vector or validated data")
        
        # Evaluate policy
        policy_report = evaluate_policy(state['feature_vector'], state['validated_data'])
        
        # Log audit entry
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        audit_trail.append(AuditEntry(
            component="policy_engine",
            timestamp=datetime.now(),
            duration_ms=duration_ms,
            input_summary={"features": len(state['feature_vector'].values)},
            output_summary={"eligibility": policy_report.eligibility, "score": policy_report.eligibility_score}
        ))
        
    except Exception as e:
        errors.append({
            "component": "policy_engine",
            "error": str(e)
        })
    
    return {
        "policy_report": policy_report,
        "errors": errors,
        "audit_trail": audit_trail
    }


async def fraud_engine_node(state: AgentState) -> dict:
    """Node 3b: Detect fraud patterns (runs in parallel with policy_engine)."""
    start_time = datetime.now()
    fraud_report = None
    errors = []
    audit_trail = []
    
    try:
        if state['validated_data'] is None:
            raise ValueError("No validated data available")
        
        # Detect fraud
        fraud_report = detect_fraud(state['validated_data'], state['all_registered_accounts'])
        
        # Log audit entry
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        audit_trail.append(AuditEntry(
            component="fraud_engine",
            timestamp=datetime.now(),
            duration_ms=duration_ms,
            input_summary={"gstin": state['input'].gstin},
            output_summary={"requires_review": fraud_report.requires_manual_review, "flags": len([f for f in fraud_report.flags if f.status is True])}
        ))
        
    except Exception as e:
        errors.append({
            "component": "fraud_engine",
            "error": str(e)
        })
    
    return {
        "fraud_report": fraud_report,
        "errors": errors,
        "audit_trail": audit_trail
    }


async def predict_risk_node(state: AgentState) -> dict:
    """Node 4: Predict risk using ML model."""
    start_time = datetime.now()
    risk_prediction = None
    errors = []
    audit_trail = []
    
    try:
        if state['feature_vector'] is None:
            raise ValueError("No feature vector available")
        
        # Convert to numpy array
        features_array = np.array(state['feature_vector'].values)
        
        # Predict
        prediction = state['model'].predict(features_array)
        risk_prediction = prediction
        
        # Log audit entry
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        audit_trail.append(AuditEntry(
            component="predict_risk",
            timestamp=datetime.now(),
            duration_ms=duration_ms,
            input_summary={"features": features_array.tolist()},
            output_summary={"risk_score": prediction.risk_score, "category": prediction.risk_category.value}
        ))
        
    except Exception as e:
        errors.append({
            "component": "predict_risk",
            "error": str(e)
        })
    
    return {
        "risk_prediction": risk_prediction,
        "errors": errors,
        "audit_trail": audit_trail
    }


async def explain_shap_node(state: AgentState) -> dict:
    """Node 5: Generate SHAP explanation."""
    start_time = datetime.now()
    shap_explanation = None
    errors = []
    audit_trail = []
    
    try:
        if state['feature_vector'] is None or state['model'] is None:
            raise ValueError("Missing feature vector or model")
        
        # Generate SHAP explanation
        features_array = np.array(state['feature_vector'].values)
        shap_exp = explain(state['model'], features_array)
        shap_explanation = shap_exp
        
        # Log audit entry
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        audit_trail.append(AuditEntry(
            component="explain_shap",
            timestamp=datetime.now(),
            duration_ms=duration_ms,
            input_summary={"features": len(state['feature_vector'].values)},
            output_summary={"base_value": shap_exp.base_value, "top_features": len(shap_exp.top_5_features)}
        ))
        
    except Exception as e:
        # Non-critical - continue without explanation
        errors.append({
            "component": "explain_shap",
            "error": str(e),
            "severity": "warning"
        })
    
    return {
        "shap_explanation": shap_explanation,
        "errors": errors,
        "audit_trail": audit_trail
    }


async def reason_gemini_node(state: AgentState) -> dict:
    """Node 6: Generate LLM reasoning."""
    start_time = datetime.now()
    gemini_reasoning = None
    errors = []
    audit_trail = []
    
    try:
        if state['risk_prediction'] is None or state['shap_explanation'] is None:
            raise ValueError("Missing prediction or SHAP explanation")
        
        if state['policy_report'] is None or state['fraud_report'] is None:
            raise ValueError("Missing policy or fraud report")
        
        # Generate reasoning
        gemini_result = await reason(
            state['risk_prediction'],
            state['shap_explanation'],
            state['policy_report'],
            state['fraud_report']
        )
        gemini_reasoning = gemini_result
        
        # Log audit entry
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        audit_trail.append(AuditEntry(
            component="reason_gemini",
            timestamp=datetime.now(),
            duration_ms=duration_ms,
            input_summary={"risk_score": state['risk_prediction'].risk_score},
            output_summary={"recommendation": gemini_result.recommendation.value, "is_fallback": gemini_result.is_fallback}
        ))
        
    except Exception as e:
        # Non-critical - fallback handled in reason() function
        errors.append({
            "component": "reason_gemini",
            "error": str(e),
            "severity": "warning"
        })
    
    return {
        "gemini_reasoning": gemini_reasoning,
        "errors": errors,
        "audit_trail": audit_trail
    }


async def compile_report_node(state: AgentState) -> dict:
    """Node 7: Compile final assessment report."""
    start_time = datetime.now()
    financial_health_score = None
    confidence_breakdown = None
    final_report = None
    errors = []
    audit_trail = []
    
    try:
        # Compute composite scores
        if state['feature_vector']:
            financial_health_score = compute_financial_health_score(state['feature_vector'])
        
        if state['validated_data'] and state['risk_prediction'] and state['feature_vector']:
            confidence_breakdown = compute_confidence(
                state['validated_data'].data_sources_available,
                state['risk_prediction'],
                state['feature_vector']
            )
        
        # Compile final report
        report = AssessmentReport(
            request_id=state['request_id'],
            timestamp=datetime.now(),
            api_version="v1",
            msme_identifier=state['input'].gstin,
            risk_score=state['risk_prediction'].risk_score if state['risk_prediction'] else 0.0,
            probability_of_default=state['risk_prediction'].probability_of_default if state['risk_prediction'] else 1.0,
            risk_category=state['risk_prediction'].risk_category if state['risk_prediction'] else "HIGH",
            eligibility=state['policy_report'].eligibility if state['policy_report'] else False,
            financial_health_score=financial_health_score.overall_score if financial_health_score else 0.0,
            confidence_level=confidence_breakdown.overall_confidence if confidence_breakdown else 0.0,
            fraud_flags=state['fraud_report'].flags if state['fraud_report'] else [],
            policy_violations=state['policy_report'].violations if state['policy_report'] else [],
            top_features=state['shap_explanation'].top_5_features if state['shap_explanation'] else [],
            explanation=state['gemini_reasoning'].explanation if state['gemini_reasoning'] else "Assessment incomplete",
            recommendation=state['gemini_reasoning'].recommendation if state['gemini_reasoning'] else "MANUAL_REVIEW",
            audit_trail_id=state['request_id']
        )
        
        final_report = report
        
        # Log audit entry
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        audit_trail.append(AuditEntry(
            component="compile_report",
            timestamp=datetime.now(),
            duration_ms=duration_ms,
            input_summary={"components_completed": len(state['audit_trail'])},
            output_summary={"recommendation": report.recommendation.value, "risk_score": report.risk_score}
        ))
        
    except Exception as e:
        errors.append({
            "component": "compile_report",
            "error": str(e)
        })
    
    return {
        "financial_health_score": financial_health_score,
        "confidence_breakdown": confidence_breakdown,
        "final_report": final_report,
        "errors": errors,
        "audit_trail": audit_trail
    }


# ============================================================================
# Workflow Construction
# ============================================================================

def create_workflow() -> StateGraph:
    """Create and configure the LangGraph workflow.
    
    Returns:
        Compiled StateGraph ready for execution
    """
    # Initialize graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("validate_data", validate_data_node)
    workflow.add_node("engineer_features", engineer_features_node)
    workflow.add_node("policy_engine", policy_engine_node)
    workflow.add_node("fraud_engine", fraud_engine_node)
    workflow.add_node("predict_risk", predict_risk_node)
    workflow.add_node("explain_shap", explain_shap_node)
    workflow.add_node("reason_gemini", reason_gemini_node)
    workflow.add_node("compile_report", compile_report_node)
    
    # Define edges (sequential and parallel execution)
    workflow.set_entry_point("validate_data")
    workflow.add_edge("validate_data", "engineer_features")
    
    # Parallel execution: policy_engine AND fraud_engine
    workflow.add_edge("engineer_features", "policy_engine")
    workflow.add_edge("engineer_features", "fraud_engine")
    
    # Fan-in to predict_risk (waits for both policy and fraud)
    workflow.add_edge("policy_engine", "predict_risk")
    workflow.add_edge("fraud_engine", "predict_risk")
    
    # Sequential after prediction
    workflow.add_edge("predict_risk", "explain_shap")
    workflow.add_edge("explain_shap", "reason_gemini")
    workflow.add_edge("reason_gemini", "compile_report")
    workflow.add_edge("compile_report", END)
    
    # Compile and return
    return workflow.compile()


# ============================================================================
# Main Execution Function
# ============================================================================

async def evaluate_msme(msme_input: MSMEInput, all_registered_accounts: Optional[set] = None) -> AssessmentReport:
    """Execute complete risk assessment workflow.
    
    Args:
        msme_input: MSME application data
        all_registered_accounts: Set of bank accounts seen in other applications
        
    Returns:
        AssessmentReport with complete risk assessment
        
    Raises:
        ValueError: If critical components fail
    """
    # Load model
    model = load_model()
    
    # Initialize state
    initial_state = AgentState(
        input=msme_input,
        request_id=str(uuid.uuid4()),
        validated_data=None,
        feature_vector=None,
        policy_report=None,
        fraud_report=None,
        risk_prediction=None,
        shap_explanation=None,
        gemini_reasoning=None,
        financial_health_score=None,
        confidence_breakdown=None,
        final_report=None,
        errors=[],
        audit_trail=[],
        model=model,
        all_registered_accounts=all_registered_accounts or set()
    )
    
    # Create and execute workflow
    workflow = create_workflow()
    result_state = await workflow.ainvoke(initial_state)
    
    # Check for critical errors
    critical_errors = [e for e in result_state['errors'] if e.get('severity') != 'warning']
    if critical_errors:
        raise ValueError(f"Workflow failed: {critical_errors}")
    
    # Return final report
    if result_state['final_report'] is None:
        raise ValueError("Workflow completed but no report generated")
    
    return result_state['final_report']
