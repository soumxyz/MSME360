"""Pydantic data models for Risk Intelligence Agent.

This module defines all data models used throughout the Risk Intelligence Agent
using Pydantic v2 for validation and serialization.
"""

from datetime import datetime, date
from typing import Optional, Literal, Annotated
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict
import re


# ============================================================================
# Input Models
# ============================================================================

class UPITransaction(BaseModel):
    """Individual UPI transaction record."""
    amount: Annotated[float, Field(gt=0, description="Transaction amount in INR, positive float with max 2 decimal places")]
    timestamp: datetime
    counterparty: str
    
    @field_validator('amount')
    @classmethod
    def validate_amount_decimals(cls, v: float) -> float:
        """Ensure amount has maximum 2 decimal places."""
        if round(v, 2) != v:
            raise ValueError('Amount must have maximum 2 decimal places')
        return v


class GSTData(BaseModel):
    """GST data including revenue, filing history, and invoices."""
    gstin: str
    monthly_revenue: list[float]  # Chronological order, oldest first
    filing_history: list[bool]    # True = filed on time
    annual_turnover: float
    
    @field_validator('gstin')
    @classmethod
    def validate_gstin_format(cls, v: str) -> str:
        """Validate GSTIN format matches required pattern."""
        pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        if not re.match(pattern, v):
            raise ValueError(f'GSTIN format invalid: {v}')
        return v


class AccountAggregatorData(BaseModel):
    """Bank statement data from Account Aggregator."""
    month_end_balances: list[float]
    monthly_inflows: list[float]
    monthly_outflows: list[float]
    statement_start_date: date
    statement_end_date: date
    
    @field_validator('statement_end_date')
    @classmethod
    def validate_date_range(cls, v: date, info) -> date:
        """Ensure statement spans at least 90 consecutive days."""
        if 'statement_start_date' in info.data:
            start = info.data['statement_start_date']
            days = (v - start).days
            if days < 90:
                raise ValueError(f'Bank statement must span at least 90 days, got {days} days')
        return v


class EPFOData(BaseModel):
    """Employee Provident Fund Organization data."""
    monthly_employee_counts: list[int]  # Chronological order


class BankData(BaseModel):
    """Existing loan and EMI data."""
    total_monthly_emi: float
    loan_amounts: list[float]
    account_number: str


class MSMEInput(BaseModel):
    """Top-level input model for MSME credit evaluation."""
    gstin: str
    pan: str
    business_registration_date: date
    gst_data: GSTData
    upi_transactions: list[UPITransaction]
    account_aggregator_data: AccountAggregatorData
    epfo_data: Optional[EPFOData] = None
    bank_data: Optional[BankData] = None
    
    @field_validator('pan')
    @classmethod
    def validate_pan_format(cls, v: str) -> str:
        """Validate PAN format matches required pattern."""
        pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        if not re.match(pattern, v):
            raise ValueError(f'PAN format invalid: {v}')
        return v
    
    @field_validator('gstin')
    @classmethod
    def validate_gstin_format(cls, v: str) -> str:
        """Validate GSTIN format."""
        pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        if not re.match(pattern, v):
            raise ValueError(f'GSTIN format invalid: {v}')
        return v


# ============================================================================
# Feature Vector Model
# ============================================================================

class FeatureVector(BaseModel):
    """8-element feature vector for ML prediction.
    
    Index mapping:
    0: revenue_growth_percentage
    1: average_monthly_balance
    2: cash_flow_ratio
    3: upi_transaction_frequency
    4: employee_growth_percentage
    5: emi_to_revenue_ratio
    6: business_age_months
    7: digital_payment_ratio
    
    Null/missing features are encoded as -1.0
    """
    values: Annotated[list[float], Field(min_length=8, max_length=8)]
    feature_names: list[str]
    null_flags: list[bool]  # True = feature was NULL (encoded as -1)
    
    @field_validator('values')
    @classmethod
    def validate_length(cls, v: list[float]) -> list[float]:
        """Ensure exactly 8 elements."""
        if len(v) != 8:
            raise ValueError(f'Feature vector must have exactly 8 elements, got {len(v)}')
        return v


# ============================================================================
# Validation Models
# ============================================================================

class ValidationError(BaseModel):
    """Validation error details."""
    field: str
    error: str
    value: Optional[str] = None


class ValidatedData(BaseModel):
    """Validated input data structure."""
    status: Literal["VALIDATED"]
    data: MSMEInput
    data_sources_available: list[str]


# ============================================================================
# Policy Models
# ============================================================================

class PolicyReport(BaseModel):
    """Policy evaluation report."""
    eligibility: bool
    eligibility_score: Annotated[int, Field(ge=0, le=100)]
    violations: list[str]
    applied_rules: list[str]  # Rule IDs e.g., ["POL-001", "POL-003"]
    high_debt_burden: bool = False


# ============================================================================
# Fraud Detection Models
# ============================================================================

class FraudFlag(BaseModel):
    """Individual fraud flag with details."""
    flag_name: str
    status: Optional[bool]  # None = data unavailable
    description: str


class FraudReport(BaseModel):
    """Fraud detection report."""
    gst_bank_mismatch: Optional[bool] = None
    suspicious_revenue_spike: Optional[bool] = None
    circular_transactions: Optional[bool] = None
    duplicate_account: Optional[bool] = None
    fake_invoices: Optional[bool] = None
    suspicious_upi_behavior: Optional[bool] = None
    requires_manual_review: bool
    flags: list[FraudFlag]
    error_indicators: list[str] = []


# ============================================================================
# Risk Prediction Models
# ============================================================================

class RiskCategory(str, Enum):
    """Risk classification categories."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RiskPrediction(BaseModel):
    """ML model risk prediction output."""
    probability_of_default: Annotated[float, Field(ge=0.0, le=1.0)]
    risk_score: Annotated[float, Field(ge=0.0, le=100.0)]
    risk_category: RiskCategory


# ============================================================================
# Explainability Models
# ============================================================================

class FeatureContribution(BaseModel):
    """SHAP feature contribution details."""
    feature_name: str
    feature_value: float
    shap_value: float
    impact_direction: Literal["positive", "negative"]


class SHAPExplanation(BaseModel):
    """SHAP explainability output."""
    base_value: float
    top_5_features: Annotated[list[FeatureContribution], Field(max_length=5)]
    all_shap_values: list[float]


# ============================================================================
# Reasoning Models
# ============================================================================

class Recommendation(str, Enum):
    """Final recommendation categories."""
    APPROVE = "APPROVE"
    APPROVE_WITH_CONDITIONS = "APPROVE_WITH_CONDITIONS"
    REJECT = "REJECT"
    MANUAL_REVIEW = "MANUAL_REVIEW"


class GeminiReasoning(BaseModel):
    """LLM-generated reasoning and recommendation."""
    recommendation: Recommendation
    explanation: str
    positive_factors: list[str]
    negative_factors: list[str]
    fraud_alerts: list[str] = []
    is_fallback: bool = False  # True if SHAP fallback was used


# ============================================================================
# Composite Score Models
# ============================================================================

class FinancialHealthScore(BaseModel):
    """Composite financial health assessment."""
    liquidity_score: Annotated[float, Field(ge=0.0, le=100.0)]
    growth_score: Annotated[float, Field(ge=0.0, le=100.0)]
    digital_adoption_score: Annotated[float, Field(ge=0.0, le=100.0)]
    debt_management_score: Annotated[float, Field(ge=0.0, le=100.0)]
    overall_score: Annotated[float, Field(ge=0.0, le=100.0)]


class ConfidenceBreakdown(BaseModel):
    """Confidence level breakdown."""
    data_completeness_score: Annotated[float, Field(ge=0.0, le=100.0)]
    model_confidence: Annotated[float, Field(ge=0.0, le=100.0)]
    feature_stability_score: Annotated[float, Field(ge=0.0, le=100.0)]
    overall_confidence: Annotated[float, Field(ge=0.0, le=100.0)]
    requires_manual_review: bool


# ============================================================================
# Audit Trail Models
# ============================================================================

class AuditEntry(BaseModel):
    """Single audit log entry for a component execution."""
    component: str
    timestamp: datetime
    duration_ms: float
    input_summary: dict
    output_summary: dict


class AuditTrail(BaseModel):
    """Complete audit trail for an evaluation request."""
    request_id: str
    start_timestamp: datetime
    entries: list[AuditEntry]
    input_data_sources: list[str]
    final_recommendation: Recommendation


# ============================================================================
# Assessment Report (Final Output)
# ============================================================================

class AssessmentReport(BaseModel):
    """Complete risk assessment report - final output model."""
    
    # Metadata
    request_id: str
    timestamp: datetime  # ISO 8601 format
    api_version: str
    
    # MSME Identification
    msme_identifier: str  # GSTIN
    
    # Risk Assessment
    risk_score: Annotated[float, Field(ge=0.0, le=100.0)]
    probability_of_default: Annotated[float, Field(ge=0.0, le=1.0)]
    risk_category: RiskCategory
    eligibility: bool
    
    # Composite Scores
    financial_health_score: Annotated[float, Field(ge=0.0, le=100.0)]
    confidence_level: Annotated[float, Field(ge=0.0, le=100.0)]
    
    # Flags and Violations
    fraud_flags: list[FraudFlag]
    policy_violations: list[str]
    
    # Explanation
    top_features: Annotated[list[FeatureContribution], Field(max_length=5)]
    explanation: str
    recommendation: Recommendation
    
    # Traceability
    audit_trail_id: str
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "request_id": "req_12345",
            "timestamp": "2024-01-15T10:30:00Z",
            "api_version": "v1",
            "msme_identifier": "29ABCDE1234F1Z5",
            "risk_score": 72.5,
            "probability_of_default": 0.275,
            "risk_category": "LOW",
            "eligibility": True,
            "financial_health_score": 68.3,
            "confidence_level": 85.0,
            "fraud_flags": [],
            "policy_violations": [],
            "top_features": [],
            "explanation": "The MSME shows strong creditworthiness...",
            "recommendation": "APPROVE",
            "audit_trail_id": "audit_12345"
        }
    })
