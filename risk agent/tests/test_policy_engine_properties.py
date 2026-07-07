"""Property-based tests for Policy Engine using Hypothesis.

Tests Property 5: Policy Eligibility Soundness
Validates: Requirements 3.1, 3.2, 3.4, 3.5, 3.7, 3.8, 3.9, 3.11
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from datetime import date, timedelta
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
    business_age_months=None,
    emi_to_revenue_ratio=None,
    cash_flow_ratio=None,
):
    """Create a feature vector with specific values or defaults."""
    # Default to valid values if not specified
    if business_age_months is None:
        business_age_months = 24.0  # Valid: >= 12
    if emi_to_revenue_ratio is None:
        emi_to_revenue_ratio = 0.25  # Valid: 0 <= x <= 1, x <= 0.40
    if cash_flow_ratio is None:
        cash_flow_ratio = 0.20  # Valid: positive
    
    values = [
        0.5,  # revenue_growth_percentage
        0.5,  # average_monthly_balance
        cash_flow_ratio,  # cash_flow_ratio
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


def create_validated_data(
    filing_history=None,
    loan_amounts=None,
    annual_turnover=None,
    total_monthly_emi=None,
    monthly_inflows=None,
    monthly_outflows=None,
):
    """Create ValidatedData with specific parameters."""
    if filing_history is None:
        filing_history = [True] * 12
    if loan_amounts is None:
        loan_amounts = [100000.0]
    if annual_turnover is None:
        annual_turnover = 1000000.0
    if total_monthly_emi is None:
        total_monthly_emi = 10000.0
    if monthly_inflows is None:
        monthly_inflows = [100000.0] * 6
    if monthly_outflows is None:
        monthly_outflows = [80000.0] * 6
    
    return ValidatedData(
        status="VALIDATED",
        data=MSMEInput(
            gstin="29ABCDE1234F1Z5",
            pan="ABCDE1234F",
            business_registration_date=date(2022, 1, 1),
            gst_data=GSTData(
                gstin="29ABCDE1234F1Z5",
                monthly_revenue=[100000.0] * 12,
                filing_history=filing_history,
                annual_turnover=annual_turnover,
            ),
            upi_transactions=[],
            account_aggregator_data=AccountAggregatorData(
                month_end_balances=[50000.0] * 6,
                monthly_inflows=monthly_inflows,
                monthly_outflows=monthly_outflows,
                statement_start_date=date(2023, 1, 1),
                statement_end_date=date(2023, 6, 30),
            ),
            bank_data=BankData(
                total_monthly_emi=total_monthly_emi,
                loan_amounts=loan_amounts,
                account_number="1234567890",
            ),
        ),
        data_sources_available=["GST", "UPI", "AA", "BANK"]
    )


# Hypothesis strategies for generating test data
@st.composite
def business_age_strategy(draw):
    """Generate business age months with various violation scenarios."""
    scenario = draw(st.sampled_from([
        'null',           # POL-002: NULL → reject
        'too_young',      # POL-001: < 12 → reject
        'valid',          # >= 12 → pass
    ]))
    
    if scenario == 'null':
        return -1.0
    elif scenario == 'too_young':
        return draw(st.floats(min_value=0.0, max_value=11.99))
    else:  # valid
        return draw(st.floats(min_value=12.0, max_value=240.0))


@st.composite
def emi_to_revenue_strategy(draw):
    """Generate EMI to revenue ratio with various violation scenarios."""
    scenario = draw(st.sampled_from([
        'null',           # POL-007: NULL → reject
        'negative',       # POL-007: < 0 → reject
        'exceeds_max',    # POL-007: > 1.0 → reject
        'high_debt',      # POL-006: > 0.40 → high_debt_burden
        'valid',          # 0 <= x <= 0.40 → pass
    ]))
    
    if scenario == 'null':
        return -1.0
    elif scenario == 'negative':
        return draw(st.floats(min_value=-10.0, max_value=-0.01))
    elif scenario == 'exceeds_max':
        return draw(st.floats(min_value=1.01, max_value=10.0))
    elif scenario == 'high_debt':
        return draw(st.floats(min_value=0.41, max_value=1.0))
    else:  # valid
        return draw(st.floats(min_value=0.0, max_value=0.40))


@st.composite
def loan_to_turnover_strategy(draw):
    """Generate loan and turnover values with various violation scenarios."""
    scenario = draw(st.sampled_from([
        'null_no_bank',   # POL-005: No bank data → NULL ratio → reject
        'null_zero_turnover',  # POL-005: Zero turnover → NULL ratio → reject
        'negative',       # POL-005: negative ratio → reject
        'exceeds_max',    # POL-005: > 10.0 → reject
        'exceeds_threshold',  # POL-004: > 0.75 → reject
        'valid',          # 0 <= x <= 0.75 → pass
    ]))
    
    if scenario == 'null_no_bank':
        # Return None to signal no bank data
        return None, 1000000.0
    elif scenario == 'null_zero_turnover':
        return [100000.0], 0.0
    elif scenario == 'negative':
        # Can't really make this negative naturally, treat as invalid
        return [-100000.0], 1000000.0  # Negative loan (invalid)
    elif scenario == 'exceeds_max':
        # Ratio > 10.0: loan = 11M, turnover = 1M → 11.0
        return [11000000.0], 1000000.0
    elif scenario == 'exceeds_threshold':
        # Ratio > 0.75: loan = 800k, turnover = 1M → 0.80
        loan = draw(st.floats(min_value=760000.0, max_value=10000000.0))
        turnover = 1000000.0
        return [loan], turnover
    else:  # valid
        # Ratio <= 0.75: loan = 500k, turnover = 1M → 0.50
        loan = draw(st.floats(min_value=0.0, max_value=750000.0))
        turnover = 1000000.0
        return [loan], turnover


@st.composite
def cash_flow_strategy(draw):
    """Generate cash flow data with various violation scenarios."""
    scenario = draw(st.sampled_from([
        'insufficient_data',  # POL-009: < 3 months → reject
        'three_null',         # POL-009: 3 consecutive NULL → reject
        'three_negative',     # POL-008: 3 consecutive negative → reject
        'valid_positive',     # All positive → pass
        'mixed',              # Some negative, but not 3 consecutive → pass
    ]))
    
    if scenario == 'insufficient_data':
        # Only 2 months of data
        return [100000.0, 110000.0], [80000.0, 90000.0]
    elif scenario == 'three_null':
        # 3 consecutive months with zero inflow (NULL ratio)
        return [0.0, 0.0, 0.0, 100000.0, 110000.0, 120000.0], \
               [50000.0, 50000.0, 50000.0, 80000.0, 90000.0, 100000.0]
    elif scenario == 'three_negative':
        # 3 consecutive months with outflows > inflows
        return [100000.0, 100000.0, 100000.0, 200000.0, 200000.0, 200000.0], \
               [150000.0, 150000.0, 150000.0, 150000.0, 150000.0, 150000.0]
    elif scenario == 'valid_positive':
        # All months have positive cash flow
        inflows = [draw(st.floats(min_value=100000.0, max_value=200000.0)) for _ in range(6)]
        outflows = [inf * draw(st.floats(min_value=0.5, max_value=0.9)) for inf in inflows]
        return inflows, outflows
    else:  # mixed
        # Some negative, but not 3 consecutive
        return [100000.0, 100000.0, 200000.0, 100000.0, 100000.0, 200000.0], \
               [150000.0, 80000.0, 150000.0, 80000.0, 150000.0, 150000.0]


@st.composite
def gst_filing_strategy(draw):
    """Generate GST filing history with various scenarios."""
    scenario = draw(st.sampled_from([
        'insufficient_data',  # < 12 months → no POL-003 check
        'perfect',            # All filed on time → pass
        'shortfall_3',        # Exactly 3 missing → pass (not > 3)
        'shortfall_4_plus',   # 4+ missing → score reduction
    ]))
    
    if scenario == 'insufficient_data':
        # Only 6 months of data
        return [True] * 6
    elif scenario == 'perfect':
        return [True] * 12
    elif scenario == 'shortfall_3':
        # 9 filed out of 12 (3 missing, not > 3)
        filing = [True] * 9 + [False] * 3
        return filing
    else:  # shortfall_4_plus
        # 7 filed out of 12 (5 missing, > 3)
        num_filed = draw(st.integers(min_value=0, max_value=8))
        filing = [True] * num_filed + [False] * (12 - num_filed)
        return filing


# ============================================================================
# Property 5: Policy Eligibility Soundness
# **Validates: Requirements 3.1, 3.2, 3.4, 3.5, 3.7, 3.8, 3.9, 3.11**
# ============================================================================

@settings(max_examples=200, deadline=2000)
@given(
    business_age=business_age_strategy(),
    emi_ratio=emi_to_revenue_strategy(),
    loan_turnover=loan_to_turnover_strategy(),
    cash_flow=cash_flow_strategy(),
    gst_filing=gst_filing_strategy(),
)
def test_property_policy_eligibility_soundness(
    business_age, emi_ratio, loan_turnover, cash_flow, gst_filing
):
    """**Validates: Requirements 3.1, 3.2, 3.4, 3.5, 3.7, 3.8, 3.9, 3.11**
    
    Property 5: Policy Eligibility Soundness
    
    For any valid input:
    - If any hard-reject rule fires → eligibility = FALSE
    - If no hard-reject rule fires → eligibility = TRUE
    - eligibility is always boolean, never None
    
    Hard-reject rules:
    - POL-001: business_age_months < 12
    - POL-002: business_age_months IS NULL
    - POL-004: loan_to_turnover_ratio > 0.75
    - POL-005: invalid loan_to_turnover_ratio (NULL, < 0, > 10.0)
    - POL-007: invalid emi_to_revenue_ratio (NULL, < 0, > 1.0)
    - POL-008: negative cash flow for 3 consecutive months
    - POL-009: insufficient cash flow data for 3 consecutive months
    """
    # Unpack strategies
    loan_amounts, annual_turnover = loan_turnover
    monthly_inflows, monthly_outflows = cash_flow
    
    # Create feature vector
    features = create_feature_vector(
        business_age_months=business_age,
        emi_to_revenue_ratio=emi_ratio,
    )
    
    # Create validated data
    # Handle None bank data scenario
    if loan_amounts is None:
        raw_data = create_validated_data(
            filing_history=gst_filing,
            annual_turnover=annual_turnover,
            monthly_inflows=monthly_inflows,
            monthly_outflows=monthly_outflows,
        )
        raw_data.data.bank_data = None
    else:
        raw_data = create_validated_data(
            filing_history=gst_filing,
            loan_amounts=loan_amounts,
            annual_turnover=annual_turnover,
            monthly_inflows=monthly_inflows,
            monthly_outflows=monthly_outflows,
        )
    
    # Execute policy evaluation
    result = evaluate_policy(features, raw_data)
    
    # ========================================================================
    # Property: eligibility is always boolean, never None
    # ========================================================================
    assert isinstance(result.eligibility, bool), \
        "Eligibility must be a boolean value"
    
    # ========================================================================
    # Determine if any hard-reject rule should fire
    # ========================================================================
    hard_reject_expected = False
    
    # POL-001: business_age_months < 12
    if business_age != -1.0 and business_age < 12:
        hard_reject_expected = True
    
    # POL-002: business_age_months IS NULL
    if business_age == -1.0:
        hard_reject_expected = True
    
    # POL-004 & POL-005: loan_to_turnover_ratio checks
    if loan_amounts is None:
        # No bank data → NULL ratio → POL-005
        hard_reject_expected = True
    elif annual_turnover == 0:
        # Division by zero → NULL ratio → POL-005
        hard_reject_expected = True
    else:
        total_loan = sum(loan_amounts) if loan_amounts else 0
        # Check for negative loans (invalid)
        if any(loan < 0 for loan in loan_amounts):
            hard_reject_expected = True
        else:
            loan_to_turnover = total_loan / annual_turnover
            if loan_to_turnover < 0 or loan_to_turnover > 10.0:
                # POL-005: invalid ratio
                hard_reject_expected = True
            elif loan_to_turnover > 0.75:
                # POL-004: exceeds threshold
                hard_reject_expected = True
    
    # POL-007: invalid emi_to_revenue_ratio
    if emi_ratio == -1.0 or emi_ratio < 0 or emi_ratio > 1.0:
        hard_reject_expected = True
    
    # POL-008 & POL-009: cash flow checks
    if len(monthly_inflows) < 3 or len(monthly_outflows) < 3:
        # POL-009: insufficient data
        hard_reject_expected = True
    else:
        # Calculate monthly cash flow ratios
        cash_flow_ratios = []
        for inflow, outflow in zip(monthly_inflows, monthly_outflows):
            if inflow == 0:
                cash_flow_ratios.append(None)
            else:
                ratio = (inflow - outflow) / inflow
                cash_flow_ratios.append(ratio)
        
        # Check for 3 consecutive negative
        consecutive_negative = 0
        max_consecutive_negative = 0
        for ratio in cash_flow_ratios:
            if ratio is not None and ratio < 0:
                consecutive_negative += 1
                max_consecutive_negative = max(max_consecutive_negative, consecutive_negative)
            else:
                consecutive_negative = 0
        
        if max_consecutive_negative >= 3:
            # POL-008: 3 consecutive negative
            hard_reject_expected = True
        
        # Check for 3 consecutive NULL
        consecutive_null = 0
        max_consecutive_null = 0
        for ratio in cash_flow_ratios:
            if ratio is None:
                consecutive_null += 1
                max_consecutive_null = max(max_consecutive_null, consecutive_null)
            else:
                consecutive_null = 0
        
        if max_consecutive_null >= 3:
            # POL-009: 3 consecutive NULL
            hard_reject_expected = True
    
    # ========================================================================
    # Property: If any hard-reject rule fires → eligibility = FALSE
    # ========================================================================
    if hard_reject_expected:
        assert result.eligibility is False, \
            f"Expected eligibility=FALSE when hard-reject rule fires. " \
            f"business_age={business_age}, emi_ratio={emi_ratio}, " \
            f"loan_amounts={loan_amounts}, annual_turnover={annual_turnover}, " \
            f"inflows={monthly_inflows[:3] if len(monthly_inflows) >= 3 else monthly_inflows}, " \
            f"outflows={monthly_outflows[:3] if len(monthly_outflows) >= 3 else monthly_outflows}"
    
    # ========================================================================
    # Property: If no hard-reject rule fires → eligibility = TRUE
    # ========================================================================
    if not hard_reject_expected:
        assert result.eligibility is True, \
            f"Expected eligibility=TRUE when no hard-reject rule fires. " \
            f"business_age={business_age}, emi_ratio={emi_ratio}, " \
            f"loan_amounts={loan_amounts}, annual_turnover={annual_turnover}, " \
            f"violations={result.violations}"
    
    # ========================================================================
    # Additional consistency checks
    # ========================================================================
    
    # If eligibility is FALSE, there should be violations
    if result.eligibility is False:
        assert len(result.violations) > 0, \
            "If eligibility is FALSE, violations list should not be empty"
    
    # If eligibility is TRUE, violations should only contain soft violations (if any)
    if result.eligibility is True:
        # Check that no hard-reject violation messages are present
        hard_reject_messages = [
            "business age requirement not met",
            "business age data unavailable",
            "loan to turnover ratio exceeded",
            "invalid loan to turnover ratio",
            "invalid EMI to revenue ratio",
            "negative cash flow trend",
            "insufficient cash flow data",
        ]
        for violation in result.violations:
            assert violation not in hard_reject_messages, \
                f"Hard-reject violation '{violation}' found but eligibility is TRUE"
    
    # Eligibility score should always be in [0, 100]
    assert 0 <= result.eligibility_score <= 100, \
        f"Eligibility score {result.eligibility_score} not in [0, 100]"
    
    # Applied rules should be a non-empty list
    assert len(result.applied_rules) > 0, \
        "Applied rules list should not be empty"
    
    # High debt burden should be boolean
    assert isinstance(result.high_debt_burden, bool), \
        "high_debt_burden must be a boolean value"


# ============================================================================
# Additional Focused Property Tests
# ============================================================================

@settings(max_examples=100)
@given(business_age=st.floats(min_value=0.0, max_value=11.99))
def test_property_pol_001_business_age_less_than_12(business_age):
    """**Validates: Requirement 3.1**
    POL-001: business_age_months < 12 → eligibility = FALSE
    """
    features = create_feature_vector(business_age_months=business_age)
    raw_data = create_validated_data()
    
    result = evaluate_policy(features, raw_data)
    
    assert result.eligibility is False, \
        f"Expected eligibility=FALSE for business_age={business_age} < 12"
    assert "business age requirement not met" in result.violations


def test_property_pol_002_business_age_null():
    """**Validates: Requirement 3.2**
    POL-002: business_age_months IS NULL → eligibility = FALSE
    """
    features = create_feature_vector(business_age_months=-1.0)
    raw_data = create_validated_data()
    
    result = evaluate_policy(features, raw_data)
    
    assert result.eligibility is False, \
        "Expected eligibility=FALSE for NULL business_age"
    assert "business age data unavailable" in result.violations


@settings(max_examples=100)
@given(ratio=st.floats(min_value=0.76, max_value=10.0))
def test_property_pol_004_loan_to_turnover_exceeds_threshold(ratio):
    """**Validates: Requirement 3.4**
    POL-004: loan_to_turnover_ratio > 0.75 → eligibility = FALSE
    """
    # Create loan and turnover such that ratio > 0.75
    annual_turnover = 1000000.0
    total_loan = ratio * annual_turnover
    
    features = create_feature_vector()
    raw_data = create_validated_data(
        loan_amounts=[total_loan],
        annual_turnover=annual_turnover
    )
    
    result = evaluate_policy(features, raw_data)
    
    # Should be rejected unless ratio is invalid (> 10.0)
    if ratio > 10.0:
        assert "invalid loan to turnover ratio" in result.violations
    else:
        assert "loan to turnover ratio exceeded" in result.violations
    
    assert result.eligibility is False


def test_property_pol_005_invalid_loan_to_turnover_null():
    """**Validates: Requirement 3.5**
    POL-005: loan_to_turnover_ratio IS NULL → eligibility = FALSE
    """
    features = create_feature_vector()
    raw_data = create_validated_data()
    raw_data.data.bank_data = None  # No bank data → NULL ratio
    
    result = evaluate_policy(features, raw_data)
    
    assert result.eligibility is False
    assert "invalid loan to turnover ratio" in result.violations


@settings(max_examples=50)
@given(ratio=st.floats(min_value=-10.0, max_value=-0.01))
def test_property_pol_007_invalid_emi_negative(ratio):
    """**Validates: Requirement 3.7**
    POL-007: emi_to_revenue_ratio < 0 → eligibility = FALSE
    """
    features = create_feature_vector(emi_to_revenue_ratio=ratio)
    raw_data = create_validated_data()
    
    result = evaluate_policy(features, raw_data)
    
    assert result.eligibility is False
    assert "invalid EMI to revenue ratio" in result.violations


def test_property_pol_007_invalid_emi_null():
    """**Validates: Requirement 3.7**
    POL-007: emi_to_revenue_ratio IS NULL → eligibility = FALSE
    """
    features = create_feature_vector(emi_to_revenue_ratio=-1.0)
    raw_data = create_validated_data()
    
    result = evaluate_policy(features, raw_data)
    
    assert result.eligibility is False
    assert "invalid EMI to revenue ratio" in result.violations


def test_property_pol_008_three_consecutive_negative_cash_flow():
    """**Validates: Requirement 3.8**
    POL-008: cash flow ratio < 0 for 3 consecutive months → eligibility = FALSE
    """
    features = create_feature_vector()
    # Create 3 consecutive months with negative cash flow
    raw_data = create_validated_data(
        monthly_inflows=[100000.0] * 6,
        monthly_outflows=[150000.0, 150000.0, 150000.0, 80000.0, 80000.0, 80000.0]
    )
    
    result = evaluate_policy(features, raw_data)
    
    assert result.eligibility is False
    assert "negative cash flow trend" in result.violations


def test_property_pol_009_insufficient_cash_flow_data():
    """**Validates: Requirement 3.9**
    POL-009: cash flow data unavailable for 3 consecutive months → eligibility = FALSE
    """
    features = create_feature_vector()
    # Create 3 consecutive months with zero inflow (NULL ratio)
    raw_data = create_validated_data(
        monthly_inflows=[0.0, 0.0, 0.0, 100000.0, 100000.0, 100000.0],
        monthly_outflows=[50000.0, 50000.0, 50000.0, 80000.0, 80000.0, 80000.0]
    )
    
    result = evaluate_policy(features, raw_data)
    
    assert result.eligibility is False
    assert "insufficient cash flow data" in result.violations


@settings(max_examples=100)
@given(
    business_age=st.floats(min_value=12.0, max_value=240.0),
    emi_ratio=st.floats(min_value=0.0, max_value=0.40),
    loan_ratio=st.floats(min_value=0.0, max_value=0.75),
)
def test_property_no_hard_reject_implies_eligible(business_age, emi_ratio, loan_ratio):
    """**Validates: Requirement 3.11**
    If no hard-reject rule fires, eligibility = TRUE
    """
    # Create scenario where NO hard-reject rules fire
    annual_turnover = 1000000.0
    total_loan = loan_ratio * annual_turnover
    
    features = create_feature_vector(
        business_age_months=business_age,
        emi_to_revenue_ratio=emi_ratio,
    )
    raw_data = create_validated_data(
        loan_amounts=[total_loan],
        annual_turnover=annual_turnover,
        # Positive cash flow for all months
        monthly_inflows=[100000.0, 110000.0, 120000.0, 130000.0, 140000.0, 150000.0],
        monthly_outflows=[80000.0, 85000.0, 90000.0, 95000.0, 100000.0, 105000.0],
    )
    
    result = evaluate_policy(features, raw_data)
    
    assert result.eligibility is True, \
        f"Expected eligibility=TRUE when no hard-reject rules fire. " \
        f"business_age={business_age}, emi_ratio={emi_ratio}, loan_ratio={loan_ratio}, " \
        f"violations={result.violations}"
