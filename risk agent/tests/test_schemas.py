"""Unit tests for Pydantic schemas validation.

Validates: Requirement 2.2 / 2.18
"""

import pytest
from datetime import datetime, date
from pydantic import ValidationError

from agents.risk_intelligence_agent.schemas import (
    UPITransaction,
    GSTData,
    MSMEInput,
    FeatureVector,
    RiskCategory,
    Recommendation,
    AccountAggregatorData
)


def test_gstin_regex_validation():
    """Test GSTIN regex validation on GSTData."""
    # Valid GSTIN
    gst_data = GSTData(
        gstin="29ABCDE1234F1Z5",
        monthly_revenue=[1000.0] * 12,
        filing_history=[True] * 12,
        annual_turnover=1200.0
    )
    assert gst_data.gstin == "29ABCDE1234F1Z5"

    # Invalid GSTINs
    invalid_gstins = [
        "123",                    # Too short
        "29ABCDE1234F1Z",         # Too short (14 chars)
        "29ABCDE1234F1Z55",       # Too long (16 chars)
        "29abcde1234f1z5",        # Lowercase letters (pattern requires uppercase)
        "AAABCDE1234F1Z5",        # State code digits invalid
    ]
    for gstin in invalid_gstins:
        with pytest.raises(ValidationError):
            GSTData(
                gstin=gstin,
                monthly_revenue=[1000.0] * 12,
                filing_history=[True] * 12,
                annual_turnover=12000.0
            )


def test_pan_regex_validation():
    """Test PAN regex validation on MSMEInput."""
    # We construct minimal valid inputs for other required fields
    aa_data = AccountAggregatorData(
        month_end_balances=[100.0] * 6,
        monthly_inflows=[1000.0] * 6,
        monthly_outflows=[800.0] * 6,
        statement_start_date=date(2023, 1, 1),
        statement_end_date=date(2023, 6, 30)
    )
    gst_data = GSTData(
        gstin="29ABCDE1234F1Z5",
        monthly_revenue=[1000.0] * 12,
        filing_history=[True] * 12,
        annual_turnover=12000.0
    )

    # Valid PAN
    msme_input = MSMEInput(
        gstin="29ABCDE1234F1Z5",
        pan="ABCDE1234F",
        business_registration_date=date(2020, 1, 1),
        gst_data=gst_data,
        upi_transactions=[],
        account_aggregator_data=aa_data
    )
    assert msme_input.pan == "ABCDE1234F"

    # Invalid PANs
    invalid_pans = [
        "ABCDE1234",          # Too short
        "ABCDE1234FA",        # Too long
        "abcde1234f",         # Lowercase
        "1BCDE1234F",         # First char digit
        "ABCD12345F",         # Wrong number of letters/digits
    ]
    for pan in invalid_pans:
        with pytest.raises(ValidationError):
            MSMEInput(
                gstin="29ABCDE1234F1Z5",
                pan=pan,
                business_registration_date=date(2020, 1, 1),
                gst_data=gst_data,
                upi_transactions=[],
                account_aggregator_data=aa_data
            )


def test_upi_transaction_validation():
    """Test UPI transaction validation (positive amounts, max 2 decimals)."""
    # Valid transaction
    txn = UPITransaction(
        amount=100.50,
        timestamp=datetime.now(),
        counterparty="Alice"
    )
    assert txn.amount == 100.50

    # Invalid amounts
    invalid_amounts = [
        -10.0,      # Negative
        0.0,        # Zero
        100.555,    # 3 decimals
        100.1234,   # 4 decimals
    ]
    for amt in invalid_amounts:
        with pytest.raises(ValidationError):
            UPITransaction(
                amount=amt,
                timestamp=datetime.now(),
                counterparty="Alice"
            )


def test_feature_vector_length_constraints():
    """Test FeatureVector length constraints (exactly 8 elements)."""
    # Valid FeatureVector
    fv = FeatureVector(
        values=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
        feature_names=["f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8"],
        null_flags=[False] * 8
    )
    assert len(fv.values) == 8

    # Too few elements
    with pytest.raises(ValidationError):
        FeatureVector(
            values=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7],
            feature_names=["f1", "f2", "f3", "f4", "f5", "f6", "f7"],
            null_flags=[False] * 7
        )

    # Too many elements
    with pytest.raises(ValidationError):
        FeatureVector(
            values=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
            feature_names=["f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9"],
            null_flags=[False] * 9
        )


def test_enum_value_constraints():
    """Test enum value constraints for RiskCategory and Recommendation."""
    # Test RiskCategory values
    assert RiskCategory.LOW == "LOW"
    assert RiskCategory.MEDIUM == "MEDIUM"
    assert RiskCategory.HIGH == "HIGH"
    
    with pytest.raises(ValueError):
        RiskCategory("INVALID")

    # Test Recommendation values
    assert Recommendation.APPROVE == "APPROVE"
    assert Recommendation.APPROVE_WITH_CONDITIONS == "APPROVE_WITH_CONDITIONS"
    assert Recommendation.REJECT == "REJECT"
    assert Recommendation.MANUAL_REVIEW == "MANUAL_REVIEW"

    with pytest.raises(ValueError):
        Recommendation("INVALID")
