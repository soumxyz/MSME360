"""Property-based tests for Policy Engine Module.

Tests policy eligibility soundness and rule evaluation logic.
Validates Requirements 3.1, 3.2, 3.4, 3.5, 3.7, 3.8, 3.9, 3.11 from the specification.
"""

import pytest
from datetime import date, datetime, timedelta
from hypothesis import given, strategies as st, settings, assume, HealthCheck
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
# Hypothesis Strategies for Input Generation
# ============================================================================

@st.composite
def valid_gstin(draw):
    """Generate a valid GSTIN matching the pattern."""
    state_code = draw(st.integers(min_value=10, max_value=99))
    # Generate exactly 5 uppercase letters A-Z
    pan_chars = ''.join([draw(st.sampled_from('ABCDEFGHIJKLMNOPQRSTUVWXYZ')) for _ in range(5)])
    entity_number = draw(st.integers(min_value=1000, max_value=9999))
    entity_type = draw(st.sampled_from(['A', 'B', 'C', 'F', 'G', 'H', 'L', 'J', 'P', 'T']))
    check_digit = draw(st.sampled_from(['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']))
    final_char = draw(st.sampled_from([str(i) for i in range(10)] + list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')))
    
    return f"{state_code}{pan_chars}{entity_number}{entity_type}{check_digit}Z{final_char}"


@st.composite
def valid_pan(draw):
    """Generate a valid PAN matching the pattern."""
    # Generate exactly 5 uppercase letters A-Z
    pan_chars = ''.join([draw(st.sampled_from('ABCDEFGHIJKLMNOPQRSTUVWXYZ')) for _ in range(5)])
    digits = draw(st.integers(min_value=1000, max_value=9999))
    last_char = draw(st.sampled_from('ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
    
    return f"{pan_chars}{digits}{last_char}"


@st.composite
def feature_vector_strategy(draw, 
                           business_age_null=False,
                           business_age_low=False,
                           emi_ratio_null=False,
                           emi_ratio_high=False,
                           emi_ratio_invalid=False):
    """Generate a FeatureVector with configurable business age and EMI ratio.
    
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
    # Generate base features (indices 0-4, 7)
    values = [
        draw(st.floats(min_value=0.0, max_value=1.0)),  # 0: revenue_growth
        draw(st.floats(min_value=0.0, max_value=1.0)),  # 1: avg_balance
        draw(st.floats(min_value=0.0, max_value=1.0)),  # 2: cash_flow
        draw(st.floats(min_value=0.0, max_value=1.0)),  # 3: upi_freq
        draw(st.floats(min_value=0.0, max_value=1.0)),  # 4: employee_growth
    ]
    
    # Index 5: emi_to_revenue_ratio
    if emi_ratio_null:
        emi_ratio = -1.0
    elif emi_ratio_high:
        emi_ratio = draw(st.floats(min_value=0.41, max_value=1.0))
    elif emi_ratio_invalid:
        # Invalid: negative or > 1.0
        emi_ratio = draw(st.one_of(
            st.floats(min_value=-10.0, max_value=-0.01),
            st.floats(min_value=1.01, max_value=10.0)
        ))
    else:
        emi_ratio = draw(st.floats(min_value=0.0, max_value=0.40))
    
    values.append(emi_ratio)
    
    # Index 6: business_age_months
    if business_age_null:
        business_age = -1.0
    elif business_age_low:
        business_age = draw(st.floats(min_value=0.0, max_value=11.99))
    else:
        business_age = draw(st.floats(min_value=12.0, max_value=120.0))
    
    values.append(business_age)
    
    # Index 7: digital_payment_ratio
    values.append(draw(st.floats(min_value=0.0, max_value=1.0)))
    
    feature_names = [
        'revenue_growth_percentage',
        'average_monthly_balance',
        'cash_flow_ratio',
        'upi_transaction_frequency',
        'employee_growth_percentage',
        'emi_to_revenue_ratio',
        'business_age_months',
        'digital_payment_ratio',
    ]
    
    null_flags = [v == -1.0 for v in values]
    
    return FeatureVector(
        values=values,
        feature_names=feature_names,
        null_flags=null_flags
    )


@st.composite
def validated_data_strategy(draw,
                           loan_to_turnover_high=False,
                           loan_to_turnover_invalid=False,
                           negative_cash_flow_3_months=False,
                           insufficient_cash_flow_3_months=False,
                           gst_filing_shortfall=False):
    """Generate ValidatedData with configurable policy rule violations."""
    
    gstin = draw(valid_gstin())
    pan = draw(valid_pan())
    business_reg_date = draw(st.dates(min_value=date(2018, 1, 1), max_value=date(2023, 12, 31)))
    
    # GST Data
    monthly_revenue = [draw(st.floats(min_value=50000, max_value=500000)) for _ in range(12)]
    
    if gst_filing_shortfall:
        # Create filing shortfall > 3 (e.g., only 8 filed out of 12)
        filing_history = [True] * 8 + [False] * 4
    else:
        filing_history = [draw(st.booleans()) for _ in range(12)]
        # Ensure at most 3 missing filings
        while sum(1 for f in filing_history if not f) > 3:
            filing_history[draw(st.integers(min_value=0, max_value=11))] = True
    
    annual_turnover = draw(st.floats(min_value=100000, max_value=10000000))
    
    gst_data = GSTData(
        gstin=gstin,
        monthly_revenue=monthly_revenue,
        filing_history=filing_history,
        annual_turnover=annual_turnover
    )
    
    # UPI Transactions
    upi_transactions = [
        UPITransaction(
            amount=round(draw(st.floats(min_value=100, max_value=10000)), 2),
            timestamp=datetime(2023, 1, 1) + timedelta(days=draw(st.integers(min_value=0, max_value=180))),
            counterparty=f"customer_{draw(st.integers(min_value=1, max_value=100))}"
        )
        for _ in range(draw(st.integers(min_value=10, max_value=100)))
    ]
    
    # Account Aggregator Data
    num_months = draw(st.integers(min_value=6, max_value=12))
    
    if negative_cash_flow_3_months:
        # Create 3 consecutive months with negative cash flow (outflows > inflows)
        monthly_inflows = []
        monthly_outflows = []
        for i in range(num_months):
            inflow = draw(st.floats(min_value=10000, max_value=100000))
            if i < 3:
                # First 3 months: negative cash flow
                outflow = inflow * draw(st.floats(min_value=1.1, max_value=2.0))
            else:
                outflow = inflow * draw(st.floats(min_value=0.5, max_value=0.9))
            
            monthly_inflows.append(inflow)
            monthly_outflows.append(outflow)
    elif insufficient_cash_flow_3_months:
        # Create 3 consecutive months with zero inflows (data unavailable)
        monthly_inflows = [0.0, 0.0, 0.0]
        monthly_outflows = [draw(st.floats(min_value=0, max_value=50000)) for _ in range(3)]
        for _ in range(num_months - 3):
            inflow = draw(st.floats(min_value=10000, max_value=100000))
            outflow = inflow * draw(st.floats(min_value=0.5, max_value=0.9))
            monthly_inflows.append(inflow)
            monthly_outflows.append(outflow)
    else:
        # Normal case: positive cash flow
        monthly_inflows = [draw(st.floats(min_value=10000, max_value=100000)) for _ in range(num_months)]
        monthly_outflows = [inflow * draw(st.floats(min_value=0.5, max_value=0.9)) for inflow in monthly_inflows]
    
    aa_data = AccountAggregatorData(
        month_end_balances=[draw(st.floats(min_value=5000, max_value=100000)) for _ in range(num_months)],
        monthly_inflows=monthly_inflows,
        monthly_outflows=monthly_outflows,
        statement_start_date=date(2023, 1, 1),
        statement_end_date=date(2023, 1, 1) + timedelta(days=num_months * 30)
    )
    
    # Bank Data (optional)
    if loan_to_turnover_high or loan_to_turnover_invalid:
        has_bank_data = True
    else:
        has_bank_data = draw(st.booleans())
        
    if has_bank_data:
        if loan_to_turnover_invalid:
            # Create invalid ratio: NULL (turnover = 0) or negative loan amounts
            if draw(st.booleans()):
                annual_turnover = 0.0
                loan_amounts = [draw(st.floats(min_value=10000, max_value=100000))]
            else:
                loan_amounts = [draw(st.floats(min_value=-100000, max_value=-1000))]
        elif loan_to_turnover_high:
            # Create high loan-to-turnover ratio > 0.75
            loan_amounts = [annual_turnover * draw(st.floats(min_value=0.76, max_value=2.0))]
        else:
            # Normal case: ratio <= 0.75
            loan_amounts = [annual_turnover * draw(st.floats(min_value=0.0, max_value=0.75))]
        
        bank_data = BankData(
            total_monthly_emi=draw(st.floats(min_value=1000, max_value=50000)),
            loan_amounts=loan_amounts,
            account_number=f"{draw(st.integers(min_value=1000000000, max_value=9999999999))}"
        )
    else:
        bank_data = None
    
    # EPFO Data (optional)
    has_epfo_data = draw(st.booleans())
    if has_epfo_data:
        epfo_data = EPFOData(
            monthly_employee_counts=[draw(st.integers(min_value=5, max_value=50)) for _ in range(12)]
        )
    else:
        epfo_data = None
    
    # Update GST data if we modified annual_turnover
    gst_data.annual_turnover = annual_turnover
    
    data_sources = ["GST", "UPI", "AA"]
    if bank_data:
        data_sources.append("BANK")
    if epfo_data:
        data_sources.append("EPFO")
    
    msme_input = MSMEInput(
        gstin=gstin,
        pan=pan,
        business_registration_date=business_reg_date,
        gst_data=gst_data,
        upi_transactions=upi_transactions,
        account_aggregator_data=aa_data,
        epfo_data=epfo_data,
        bank_data=bank_data
    )
    
    return ValidatedData(
        status="VALIDATED",
        data=msme_input,
        data_sources_available=data_sources
    )


# ============================================================================
# Property 5: Policy Eligibility Soundness
# **Validates: Requirements 3.1, 3.2, 3.4, 3.5, 3.7, 3.8, 3.9, 3.11**
# ============================================================================

@given(
    features=feature_vector_strategy(business_age_low=True),
    raw_data=validated_data_strategy()
)
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.large_base_example])
def test_property_business_age_low_implies_ineligible(features, raw_data):
    """**Validates: Requirements 3.1**
    
    Property: If business_age_months < 12, then eligibility = FALSE
    
    This is a hard-reject rule (POL-001).
    """
    # Business age is < 12 (configured in strategy)
    assume(features.values[6] >= 0 and features.values[6] < 12)
    
    result = evaluate_policy(features, raw_data)
    
    # Eligibility MUST be FALSE
    assert result.eligibility is False
    assert "business age requirement not met" in result.violations
    assert "POL-001" in result.applied_rules


@given(
    features=feature_vector_strategy(business_age_null=True),
    raw_data=validated_data_strategy()
)
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.large_base_example])
def test_property_business_age_null_implies_ineligible(features, raw_data):
    """**Validates: Requirements 3.2**
    
    Property: If business_age_months is NULL, then eligibility = FALSE
    
    This is a hard-reject rule (POL-002).
    """
    # Business age is NULL (-1)
    assert features.values[6] == -1.0
    
    result = evaluate_policy(features, raw_data)
    
    # Eligibility MUST be FALSE
    assert result.eligibility is False
    assert "business age data unavailable" in result.violations
    assert "POL-002" in result.applied_rules


@given(
    features=feature_vector_strategy(),
    raw_data=validated_data_strategy(loan_to_turnover_high=True)
)
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.large_base_example])
def test_property_loan_to_turnover_high_implies_ineligible(features, raw_data):
    """**Validates: Requirements 3.4**
    
    Property: If loan_to_turnover_ratio > 0.75, then eligibility = FALSE
    
    This is a hard-reject rule (POL-004).
    """
    # Ensure business age is valid (not triggering other rules)
    assume(features.values[6] >= 12.0)
    
    result = evaluate_policy(features, raw_data)
    
    # Eligibility MUST be FALSE
    assert result.eligibility is False
    assert "loan to turnover ratio exceeded" in result.violations
    assert "POL-004" in result.applied_rules


@given(
    features=feature_vector_strategy(),
    raw_data=validated_data_strategy(loan_to_turnover_invalid=True)
)
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.large_base_example])
def test_property_loan_to_turnover_invalid_implies_ineligible(features, raw_data):
    """**Validates: Requirements 3.5**
    
    Property: If loan_to_turnover_ratio is NULL, negative, or > 10, then eligibility = FALSE
    
    This is a hard-reject rule (POL-005).
    """
    # Ensure business age is valid (not triggering other rules)
    assume(features.values[6] >= 12.0)
    
    result = evaluate_policy(features, raw_data)
    
    # Eligibility MUST be FALSE
    assert result.eligibility is False
    assert "invalid loan to turnover ratio" in result.violations
    assert "POL-005" in result.applied_rules


@given(
    features=feature_vector_strategy(emi_ratio_invalid=True),
    raw_data=validated_data_strategy()
)
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.large_base_example])
def test_property_emi_ratio_invalid_implies_ineligible(features, raw_data):
    """**Validates: Requirements 3.7**
    
    Property: If emi_to_revenue_ratio is NULL, negative, or > 1.0, then eligibility = FALSE
    
    This is a hard-reject rule (POL-007).
    """
    # Ensure business age is valid (not triggering other rules)
    assume(features.values[6] >= 12.0)
    
    # EMI ratio is invalid (configured in strategy)
    emi_ratio = features.values[5]
    assume(emi_ratio == -1.0 or emi_ratio < 0 or emi_ratio > 1.0)
    
    result = evaluate_policy(features, raw_data)
    
    # Eligibility MUST be FALSE
    assert result.eligibility is False
    assert "invalid EMI to revenue ratio" in result.violations
    assert "POL-007" in result.applied_rules


@given(
    features=feature_vector_strategy(),
    raw_data=validated_data_strategy(negative_cash_flow_3_months=True)
)
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.large_base_example])
def test_property_negative_cash_flow_3_months_implies_ineligible(features, raw_data):
    """**Validates: Requirements 3.8**
    
    Property: If cash_flow_ratio < 0 for 3 consecutive months, then eligibility = FALSE
    
    This is a hard-reject rule (POL-008).
    """
    # Ensure business age is valid (not triggering other rules)
    assume(features.values[6] >= 12.0)
    # Ensure EMI ratio is valid
    emi_ratio = features.values[5]
    assume(emi_ratio >= 0 and emi_ratio <= 1.0)
    
    result = evaluate_policy(features, raw_data)
    
    # Eligibility MUST be FALSE
    assert result.eligibility is False
    assert "negative cash flow trend" in result.violations
    assert "POL-008" in result.applied_rules


@given(
    features=feature_vector_strategy(),
    raw_data=validated_data_strategy(insufficient_cash_flow_3_months=True)
)
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.large_base_example])
def test_property_insufficient_cash_flow_3_months_implies_ineligible(features, raw_data):
    """**Validates: Requirements 3.9**
    
    Property: If cash_flow_ratio unavailable for 3 consecutive months, then eligibility = FALSE
    
    This is a hard-reject rule (POL-009).
    """
    # Ensure business age is valid (not triggering other rules)
    assume(features.values[6] >= 12.0)
    # Ensure EMI ratio is valid
    emi_ratio = features.values[5]
    assume(emi_ratio >= 0 and emi_ratio <= 1.0)
    
    result = evaluate_policy(features, raw_data)
    
    # Eligibility MUST be FALSE
    assert result.eligibility is False
    assert "insufficient cash flow data" in result.violations
    assert "POL-009" in result.applied_rules


@given(
    features=feature_vector_strategy(),
    raw_data=validated_data_strategy()
)
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.large_base_example])
def test_property_no_hard_reject_implies_eligible(features, raw_data):
    """**Validates: Requirements 3.11**
    
    Property: If NO hard-reject rule fires, then eligibility = TRUE
    
    Hard-reject rules: POL-001, POL-002, POL-004, POL-005, POL-007, POL-008, POL-009
    """
    # Ensure business age is valid (>= 12)
    assume(features.values[6] >= 12.0)
    
    # Ensure EMI ratio is valid (0 to 1.0, not -1)
    emi_ratio = features.values[5]
    assume(emi_ratio >= 0 and emi_ratio <= 1.0)
    
    # Ensure no bank data or valid loan-to-turnover ratio
    assume(raw_data.data.bank_data is not None)
    annual_turnover = raw_data.data.gst_data.annual_turnover
    if annual_turnover > 0:
        loan_amounts = raw_data.data.bank_data.loan_amounts
        total_loan = sum(loan_amounts) if loan_amounts else 0
        loan_to_turnover = total_loan / annual_turnover
        assume(loan_to_turnover >= 0 and loan_to_turnover <= 0.75)
    
    # Ensure no negative cash flow for 3 consecutive months
    aa_data = raw_data.data.account_aggregator_data
    monthly_inflows = aa_data.monthly_inflows
    monthly_outflows = aa_data.monthly_outflows
    
    # Calculate cash flow ratios
    cash_flow_ratios = []
    for inflow, outflow in zip(monthly_inflows, monthly_outflows):
        if inflow > 0:
            ratio = (inflow - outflow) / inflow
            cash_flow_ratios.append(ratio)
        else:
            cash_flow_ratios.append(None)
    
    # Check for 3 consecutive negative cash flows
    consecutive_negative = 0
    max_consecutive_negative = 0
    for ratio in cash_flow_ratios:
        if ratio is not None and ratio < 0:
            consecutive_negative += 1
            max_consecutive_negative = max(max_consecutive_negative, consecutive_negative)
        else:
            consecutive_negative = 0
    
    assume(max_consecutive_negative < 3)
    
    # Check for 3 consecutive null cash flows
    consecutive_null = 0
    max_consecutive_null = 0
    for ratio in cash_flow_ratios:
        if ratio is None:
            consecutive_null += 1
            max_consecutive_null = max(max_consecutive_null, consecutive_null)
        else:
            consecutive_null = 0
    
    assume(max_consecutive_null < 3)
    
    result = evaluate_policy(features, raw_data)
    
    # Eligibility MUST be TRUE
    assert result.eligibility is True


@given(
    features=feature_vector_strategy(),
    raw_data=validated_data_strategy()
)
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.large_base_example])
def test_property_eligibility_is_always_boolean(features, raw_data):
    """**Validates: General soundness**
    
    Property: Eligibility is always a boolean value, never None
    """
    result = evaluate_policy(features, raw_data)
    
    assert isinstance(result.eligibility, bool)
    assert result.eligibility is not None


@given(
    features=feature_vector_strategy(),
    raw_data=validated_data_strategy()
)
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.large_base_example])
def test_property_eligibility_soundness_comprehensive(features, raw_data):
    """**Validates: Requirements 3.1, 3.2, 3.4, 3.5, 3.7, 3.8, 3.9, 3.11**
    
    Property: Eligibility is FALSE if and only if at least one hard-reject rule fires
    
    This is the main soundness property that encompasses all hard-reject rules.
    """
    result = evaluate_policy(features, raw_data)
    
    # Determine if any hard-reject rule should fire
    business_age = features.values[6]
    emi_ratio = features.values[5]
    
    hard_reject_fired = False
    
    # POL-001: business_age < 12
    if business_age >= 0 and business_age < 12:
        hard_reject_fired = True
    
    # POL-002: business_age is NULL
    if business_age == -1.0:
        hard_reject_fired = True
    
    # POL-007: EMI ratio invalid
    if emi_ratio == -1.0 or emi_ratio < 0 or emi_ratio > 1.0:
        hard_reject_fired = True
    
    # POL-004, POL-005: Loan-to-turnover ratio
    if raw_data.data.bank_data is None:
        # missing bank data -> NULL ratio -> POL-005
        hard_reject_fired = True
    else:
        annual_turnover = raw_data.data.gst_data.annual_turnover
        loan_amounts = raw_data.data.bank_data.loan_amounts
        total_loan = sum(loan_amounts) if loan_amounts else 0
        
        if annual_turnover == 0:
            # POL-005: Invalid ratio (NULL)
            hard_reject_fired = True
        elif total_loan < 0:
            # POL-005: Invalid ratio (negative)
            hard_reject_fired = True
        else:
            loan_to_turnover = total_loan / annual_turnover
            if loan_to_turnover > 10.0:
                # POL-005: Invalid ratio (> 10)
                hard_reject_fired = True
            elif loan_to_turnover > 0.75:
                # POL-004: Exceeds threshold
                hard_reject_fired = True
    
    # POL-008, POL-009: Cash flow violations
    aa_data = raw_data.data.account_aggregator_data
    monthly_inflows = aa_data.monthly_inflows
    monthly_outflows = aa_data.monthly_outflows
    
    cash_flow_ratios = []
    for inflow, outflow in zip(monthly_inflows, monthly_outflows):
        if inflow > 0:
            ratio = (inflow - outflow) / inflow
            cash_flow_ratios.append(ratio)
        else:
            cash_flow_ratios.append(None)
    
    # Check POL-008: 3 consecutive negative
    consecutive_negative = 0
    for ratio in cash_flow_ratios:
        if ratio is not None and ratio < 0:
            consecutive_negative += 1
            if consecutive_negative >= 3:
                hard_reject_fired = True
                break
        else:
            consecutive_negative = 0
    
    # Check POL-009: 3 consecutive null
    consecutive_null = 0
    for ratio in cash_flow_ratios:
        if ratio is None:
            consecutive_null += 1
            if consecutive_null >= 3:
                hard_reject_fired = True
                break
        else:
            consecutive_null = 0
    
    # Verify the property: eligibility = FALSE iff hard_reject_fired
    if hard_reject_fired:
        assert result.eligibility is False, \
            f"Expected eligibility=FALSE when hard-reject rule fired. violations={result.violations}"
    else:
        assert result.eligibility is True, \
            f"Expected eligibility=TRUE when no hard-reject rule fired. violations={result.violations}"
