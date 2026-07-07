"""Property-based tests for eligibility score bounds using Hypothesis.

Tests Property 6: Eligibility Score Non-Negative
Validates: Requirements 3.10, 3.12
"""

import pytest
import sys
from pathlib import Path
from hypothesis import given, strategies as st, assume, settings
from datetime import date, timedelta

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.risk_intelligence_agent.policy_engine import evaluate_policy
from agents.risk_intelligence_agent.schemas import (
    FeatureVector,
    ValidatedData,
    MSMEInput,
    GSTData,
    UPITransaction,
    AccountAggregatorData,
    EPFOData,
    BankData,
    PolicyReport,
)


# ============================================================================
# Strategy Definitions
# ============================================================================

def create_feature_vector(
    business_age_months=24.0,
    emi_to_revenue_ratio=0.25,
):
    """Create a feature vector with specific values or defaults."""
    values = [
        0.5,  # revenue_growth_percentage
        0.5,  # average_monthly_balance
        0.2,  # cash_flow_ratio
        0.5,  # upi_transaction_frequency
        0.5,  # employee_growth_percentage
        emi_to_revenue_ratio,  # emi_to_revenue_ratio
        business_age_months,  # business_age_months
        0.5,  # digital_payment_ratio
    ]
    
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
            'digital_payment_ratio',
        ],
        null_flags=[v == -1.0 for v in values]
    )


@st.composite
def gst_filing_history_strategy(draw):
    """Generate GST filing history with various shortfall scenarios.
    
    POL-003 fires when: filing_shortfall > 3 (i.e., expected - actual > 3)
    This means: filed < 9 out of 12 → score reduction of 20
    
    Strategy:
    - Generate histories that may trigger POL-003 multiple times conceptually
    - Focus on edge cases: exactly 3 missing, 4 missing, 5+ missing
    - Also test insufficient data (< 12 months)
    """
    scenario = draw(st.sampled_from([
        'insufficient_data',  # < 12 months → no check
        'no_shortfall',       # 12/12 or 11/12 or 10/12 or 9/12 filed → no reduction
        'shortfall_exactly_4',  # 8/12 filed → shortfall = 4 → reduction
        'shortfall_5',        # 7/12 filed → shortfall = 5 → reduction
        'shortfall_6',        # 6/12 filed → shortfall = 6 → reduction
        'extreme_shortfall',  # 0-5 filed → shortfall 7-12 → reduction
    ]))
    
    if scenario == 'insufficient_data':
        # Generate 0-11 months of data
        months = draw(st.integers(min_value=0, max_value=11))
        return [draw(st.booleans()) for _ in range(months)]
    elif scenario == 'no_shortfall':
        # Generate 9-12 filed out of 12
        num_filed = draw(st.integers(min_value=9, max_value=12))
        filing = [True] * num_filed + [False] * (12 - num_filed)
        return filing
    elif scenario == 'shortfall_exactly_4':
        # 8 filed out of 12 → shortfall = 4
        filing = [True] * 8 + [False] * 4
        return filing
    elif scenario == 'shortfall_5':
        # 7 filed out of 12 → shortfall = 5
        filing = [True] * 7 + [False] * 5
        return filing
    elif scenario == 'shortfall_6':
        # 6 filed out of 12 → shortfall = 6
        filing = [True] * 6 + [False] * 6
        return filing
    else:  # extreme_shortfall
        # 0-5 filed out of 12 → shortfall 7-12
        num_filed = draw(st.integers(min_value=0, max_value=5))
        filing = [True] * num_filed + [False] * (12 - num_filed)
        return filing


@st.composite
def validated_data_strategy(draw):
    """Generate ValidatedData with various GST filing scenarios.
    
    This strategy ensures all other policy checks pass (no hard-rejects),
    so we can focus on testing eligibility_score bounds with soft-reject violations.
    """
    filing_history = draw(gst_filing_history_strategy())
    
    # Ensure no hard-reject rules fire
    # - Business age: >= 12 months
    # - Loan-to-turnover: valid and <= 0.75
    # - EMI-to-revenue: valid and in [0, 1]
    # - Cash flow: sufficient and no 3 consecutive negative/null
    
    return ValidatedData(
        status="VALIDATED",
        data=MSMEInput(
            gstin="29ABCDE1234F1Z5",
            pan="ABCDE1234F",
            business_registration_date=date(2020, 1, 1),  # Old enough
            gst_data=GSTData(
                gstin="29ABCDE1234F1Z5",
                monthly_revenue=[100000.0] * 12,
                filing_history=filing_history,
                annual_turnover=1000000.0,
            ),
            upi_transactions=[],
            account_aggregator_data=AccountAggregatorData(
                month_end_balances=[50000.0] * 6,
                # Positive cash flow for all months
                monthly_inflows=[100000.0, 110000.0, 120000.0, 130000.0, 140000.0, 150000.0],
                monthly_outflows=[80000.0, 85000.0, 90000.0, 95000.0, 100000.0, 105000.0],
                statement_start_date=date(2023, 1, 1),
                statement_end_date=date(2023, 6, 30),
            ),
            bank_data=BankData(
                total_monthly_emi=10000.0,
                loan_amounts=[500000.0],  # 0.5 loan-to-turnover ratio
                account_number="1234567890",
            ),
        ),
        data_sources_available=["GST", "UPI", "AA", "BANK"]
    )


# ============================================================================
# Property 6: Eligibility Score Non-Negative
# **Validates: Requirements 3.10, 3.12**
# ============================================================================

@settings(max_examples=150, deadline=2000)
@given(
    raw_data=validated_data_strategy(),
    business_age=st.floats(min_value=12.0, max_value=240.0),
    emi_ratio=st.floats(min_value=0.0, max_value=1.0),
)
def test_property_eligibility_score_bounds(raw_data, business_age, emi_ratio):
    """**Validates: Requirements 3.10, 3.12**
    
    Property 6: Eligibility Score Non-Negative
    
    For any valid input that doesn't trigger hard-reject rules:
    - eligibility_score MUST be in the range [0, 100]
    - eligibility_score MUST be an integer
    - Score reductions (from soft-reject rules) NEVER produce negative values
    - Score starts at 100 and can only decrease
    
    Soft-reject rules:
    - POL-003: GST filing shortfall > 3 → eligibility_score -= 20
    - POL-006: EMI-to-revenue ratio > 0.40 → high_debt_burden = TRUE (no score impact)
    
    Note: Currently only POL-003 affects eligibility_score.
    """
    # Create feature vector with valid values (no hard-reject triggers)
    features = create_feature_vector(
        business_age_months=business_age,
        emi_to_revenue_ratio=emi_ratio,
    )
    
    # Execute policy evaluation
    result = evaluate_policy(features, raw_data)
    
    # ========================================================================
    # Property 1: eligibility_score is in [0, 100]
    # ========================================================================
    assert 0 <= result.eligibility_score <= 100, \
        f"Eligibility score {result.eligibility_score} is outside [0, 100] range. " \
        f"Filing history: {raw_data.data.gst_data.filing_history}, " \
        f"Violations: {result.violations}"
    
    # ========================================================================
    # Property 2: eligibility_score is an integer
    # ========================================================================
    assert isinstance(result.eligibility_score, int), \
        f"Eligibility score {result.eligibility_score} is not an integer"
    
    # ========================================================================
    # Property 3: Score never goes below 0 (floor enforcement)
    # ========================================================================
    # This is implicitly tested by Property 1, but we verify the logic
    # Count expected score reductions
    filing_history = raw_data.data.gst_data.filing_history
    expected_score = 100
    
    if len(filing_history) >= 12:
        # Check POL-003
        recent_filings = filing_history[-12:]
        gst_filing_count = sum(1 for filed in recent_filings if filed)
        expected_filing_count = 12
        shortfall = expected_filing_count - gst_filing_count
        
        if shortfall > 3:
            expected_score = max(0, expected_score - 20)
    
    # Verify the score matches expected calculation
    assert result.eligibility_score == expected_score, \
        f"Expected eligibility_score={expected_score}, got {result.eligibility_score}. " \
        f"Filing history (last 12): {filing_history[-12:] if len(filing_history) >= 12 else filing_history}, " \
        f"Shortfall: {12 - sum(filing_history[-12:]) if len(filing_history) >= 12 else 'N/A'}"
    
    # ========================================================================
    # Property 4: Score can only decrease from 100
    # ========================================================================
    assert result.eligibility_score <= 100, \
        f"Eligibility score {result.eligibility_score} exceeds maximum of 100"
    
    # ========================================================================
    # Additional consistency checks
    # ========================================================================
    
    # If score was reduced, POL-003 should be in applied_rules
    if result.eligibility_score < 100:
        assert "POL-003" in result.applied_rules, \
            "POL-003 should be in applied_rules when score is reduced"
        assert "GST filing shortfall exceeds threshold" in result.violations, \
            "GST filing shortfall violation should be present when score is reduced"


# ============================================================================
# Edge Case Tests
# ============================================================================

def test_eligibility_score_multiple_violations_scenario():
    """**Validates: Requirements 3.10, 3.12**
    
    Test edge case: Multiple soft-reject violations in a single evaluation.
    Currently only POL-003 affects score, so this tests extreme GST shortfalls.
    """
    # Extreme case: 0 out of 12 GST filings
    filing_history = [False] * 12
    
    features = create_feature_vector()
    raw_data = ValidatedData(
        status="VALIDATED",
        data=MSMEInput(
            gstin="29ABCDE1234F1Z5",
            pan="ABCDE1234F",
            business_registration_date=date(2020, 1, 1),
            gst_data=GSTData(
                gstin="29ABCDE1234F1Z5",
                monthly_revenue=[100000.0] * 12,
                filing_history=filing_history,
                annual_turnover=1000000.0,
            ),
            upi_transactions=[],
            account_aggregator_data=AccountAggregatorData(
                month_end_balances=[50000.0] * 6,
                monthly_inflows=[100000.0] * 6,
                monthly_outflows=[80000.0] * 6,
                statement_start_date=date(2023, 1, 1),
                statement_end_date=date(2023, 6, 30),
            ),
            bank_data=BankData(
                total_monthly_emi=10000.0,
                loan_amounts=[500000.0],
                account_number="1234567890",
            ),
        ),
        data_sources_available=["GST", "UPI", "AA", "BANK"]
    )
    
    result = evaluate_policy(features, raw_data)
    
    # Score should be reduced by 20 (100 - 20 = 80)
    assert result.eligibility_score == 80, \
        f"Expected score=80 for 0/12 GST filings, got {result.eligibility_score}"
    assert 0 <= result.eligibility_score <= 100
    assert isinstance(result.eligibility_score, int)


def test_eligibility_score_exactly_threshold():
    """**Validates: Requirements 3.10, 3.12**
    
    Test boundary case: GST filing shortfall exactly at threshold (3).
    """
    # Exactly 3 missing (9/12 filed) → shortfall = 3, NOT > 3 → no reduction
    filing_history = [True] * 9 + [False] * 3
    
    features = create_feature_vector()
    raw_data = ValidatedData(
        status="VALIDATED",
        data=MSMEInput(
            gstin="29ABCDE1234F1Z5",
            pan="ABCDE1234F",
            business_registration_date=date(2020, 1, 1),
            gst_data=GSTData(
                gstin="29ABCDE1234F1Z5",
                monthly_revenue=[100000.0] * 12,
                filing_history=filing_history,
                annual_turnover=1000000.0,
            ),
            upi_transactions=[],
            account_aggregator_data=AccountAggregatorData(
                month_end_balances=[50000.0] * 6,
                monthly_inflows=[100000.0] * 6,
                monthly_outflows=[80000.0] * 6,
                statement_start_date=date(2023, 1, 1),
                statement_end_date=date(2023, 6, 30),
            ),
            bank_data=BankData(
                total_monthly_emi=10000.0,
                loan_amounts=[500000.0],
                account_number="1234567890",
            ),
        ),
        data_sources_available=["GST", "UPI", "AA", "BANK"]
    )
    
    result = evaluate_policy(features, raw_data)
    
    # Score should remain 100 (shortfall not > 3)
    assert result.eligibility_score == 100, \
        f"Expected score=100 for 9/12 GST filings (shortfall=3, not > 3), got {result.eligibility_score}"


def test_eligibility_score_just_above_threshold():
    """**Validates: Requirements 3.10, 3.12**
    
    Test boundary case: GST filing shortfall just above threshold (4).
    """
    # Exactly 4 missing (8/12 filed) → shortfall = 4 > 3 → reduction
    filing_history = [True] * 8 + [False] * 4
    
    features = create_feature_vector()
    raw_data = ValidatedData(
        status="VALIDATED",
        data=MSMEInput(
            gstin="29ABCDE1234F1Z5",
            pan="ABCDE1234F",
            business_registration_date=date(2020, 1, 1),
            gst_data=GSTData(
                gstin="29ABCDE1234F1Z5",
                monthly_revenue=[100000.0] * 12,
                filing_history=filing_history,
                annual_turnover=1000000.0,
            ),
            upi_transactions=[],
            account_aggregator_data=AccountAggregatorData(
                month_end_balances=[50000.0] * 6,
                monthly_inflows=[100000.0] * 6,
                monthly_outflows=[80000.0] * 6,
                statement_start_date=date(2023, 1, 1),
                statement_end_date=date(2023, 6, 30),
            ),
            bank_data=BankData(
                total_monthly_emi=10000.0,
                loan_amounts=[500000.0],
                account_number="1234567890",
            ),
        ),
        data_sources_available=["GST", "UPI", "AA", "BANK"]
    )
    
    result = evaluate_policy(features, raw_data)
    
    # Score should be reduced to 80 (100 - 20)
    assert result.eligibility_score == 80, \
        f"Expected score=80 for 8/12 GST filings (shortfall=4 > 3), got {result.eligibility_score}"


def test_eligibility_score_insufficient_gst_data():
    """**Validates: Requirements 3.10, 3.12**
    
    Test case: Insufficient GST filing data (< 12 months).
    """
    # Only 6 months of data → POL-003 should not check
    filing_history = [False] * 6
    
    features = create_feature_vector()
    raw_data = ValidatedData(
        status="VALIDATED",
        data=MSMEInput(
            gstin="29ABCDE1234F1Z5",
            pan="ABCDE1234F",
            business_registration_date=date(2023, 6, 1),
            gst_data=GSTData(
                gstin="29ABCDE1234F1Z5",
                monthly_revenue=[100000.0] * 6,
                filing_history=filing_history,
                annual_turnover=600000.0,
            ),
            upi_transactions=[],
            account_aggregator_data=AccountAggregatorData(
                month_end_balances=[50000.0] * 6,
                monthly_inflows=[100000.0] * 6,
                monthly_outflows=[80000.0] * 6,
                statement_start_date=date(2023, 1, 1),
                statement_end_date=date(2023, 6, 30),
            ),
            bank_data=BankData(
                total_monthly_emi=10000.0,
                loan_amounts=[300000.0],
                account_number="1234567890",
            ),
        ),
        data_sources_available=["GST", "UPI", "AA", "BANK"]
    )
    
    result = evaluate_policy(features, raw_data)
    
    # Score should remain 100 (insufficient data for POL-003 check)
    assert result.eligibility_score == 100, \
        f"Expected score=100 when GST data < 12 months, got {result.eligibility_score}"
    assert 0 <= result.eligibility_score <= 100


def test_eligibility_score_perfect_gst_compliance():
    """**Validates: Requirements 3.10, 3.12**
    
    Test case: Perfect GST compliance (all filings on time).
    """
    # All 12 filings on time
    filing_history = [True] * 12
    
    features = create_feature_vector()
    raw_data = ValidatedData(
        status="VALIDATED",
        data=MSMEInput(
            gstin="29ABCDE1234F1Z5",
            pan="ABCDE1234F",
            business_registration_date=date(2020, 1, 1),
            gst_data=GSTData(
                gstin="29ABCDE1234F1Z5",
                monthly_revenue=[100000.0] * 12,
                filing_history=filing_history,
                annual_turnover=1200000.0,
            ),
            upi_transactions=[],
            account_aggregator_data=AccountAggregatorData(
                month_end_balances=[50000.0] * 6,
                monthly_inflows=[100000.0] * 6,
                monthly_outflows=[80000.0] * 6,
                statement_start_date=date(2023, 1, 1),
                statement_end_date=date(2023, 6, 30),
            ),
            bank_data=BankData(
                total_monthly_emi=10000.0,
                loan_amounts=[500000.0],
                account_number="1234567890",
            ),
        ),
        data_sources_available=["GST", "UPI", "AA", "BANK"]
    )
    
    result = evaluate_policy(features, raw_data)
    
    # Score should remain 100 (no violations)
    assert result.eligibility_score == 100, \
        f"Expected score=100 for perfect GST compliance, got {result.eligibility_score}"
    assert "GST filing shortfall exceeds threshold" not in result.violations
