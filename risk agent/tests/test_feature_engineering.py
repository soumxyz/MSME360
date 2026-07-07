"""Unit tests for Feature Engineering Module.

Tests all feature computation logic, normalization, and edge cases.
Validates Requirements 2.1-2.18 from the specification.
"""

import pytest
from datetime import datetime, date, timedelta
from agents.risk_intelligence_agent.feature_engineering import (
    engineer_features,
    _compute_revenue_growth_percentage,
    _compute_average_monthly_balance,
    _compute_cash_flow_ratio,
    _compute_upi_transaction_frequency,
    _compute_employee_growth_percentage,
    _compute_emi_to_revenue_ratio,
    _compute_business_age_months,
    _compute_digital_payment_ratio,
    _normalize,
)
from agents.risk_intelligence_agent.schemas import (
    ValidatedData,
    MSMEInput,
    GSTData,
    UPITransaction,
    AccountAggregatorData,
    EPFOData,
    BankData,
    FeatureVector,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sample_validated_data_full():
    """Create a ValidatedData object with complete 12-month data."""
    return ValidatedData(
        status="VALIDATED",
        data=MSMEInput(
            gstin="29ABCDE1234F1Z5",
            pan="ABCDE1234F",
            business_registration_date=date(2022, 1, 1),
            gst_data=GSTData(
                gstin="29ABCDE1234F1Z5",
                monthly_revenue=[100000, 105000, 110000, 115000, 120000, 125000,
                               130000, 135000, 140000, 145000, 150000, 155000],
                filing_history=[True] * 12,
                annual_turnover=1500000,
            ),
            upi_transactions=[
                UPITransaction(
                    amount=1000.50,
                    timestamp=datetime(2023, 1, 1) + timedelta(days=i * 10),
                    counterparty=f"customer_{i}"
                )
                for i in range(60)  # 600 days of data, ~20 months
            ],
            account_aggregator_data=AccountAggregatorData(
                month_end_balances=[50000, 55000, 60000, 65000, 70000, 75000],
                monthly_inflows=[200000, 210000, 220000, 230000, 240000, 250000],
                monthly_outflows=[150000, 155000, 160000, 165000, 170000, 175000],
                statement_start_date=date(2023, 1, 1),
                statement_end_date=date(2023, 6, 30),
            ),
            epfo_data=EPFOData(
                monthly_employee_counts=[10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16]
            ),
            bank_data=BankData(
                total_monthly_emi=30000,
                loan_amounts=[500000],
                account_number="1234567890",
            ),
        ),
        data_sources_available=["GST", "UPI", "AA", "EPFO", "BANK"]
    )


@pytest.fixture
def sample_validated_data_minimal():
    """Create a ValidatedData object with minimal data (insufficient for most features)."""
    return ValidatedData(
        status="VALIDATED",
        data=MSMEInput(
            gstin="29ABCDE1234F1Z5",
            pan="ABCDE1234F",
            business_registration_date=date(2023, 10, 1),
            gst_data=GSTData(
                gstin="29ABCDE1234F1Z5",
                monthly_revenue=[100000, 105000],  # Only 2 months
                filing_history=[True, True],
                annual_turnover=200000,
            ),
            upi_transactions=[
                UPITransaction(
                    amount=1000.0,
                    timestamp=datetime(2023, 11, 1),
                    counterparty="customer_1"
                )
            ],
            account_aggregator_data=AccountAggregatorData(
                month_end_balances=[50000, 55000],  # Only 2 months
                monthly_inflows=[100000, 105000],
                monthly_outflows=[80000, 85000],
                statement_start_date=date(2023, 10, 1),
                statement_end_date=date(2023, 12, 31),
            ),
            epfo_data=None,
            bank_data=None,
        ),
        data_sources_available=["GST", "UPI", "AA"]
    )


# ============================================================================
# Test Revenue Growth Percentage (Requirement 2.1, 2.2)
# ============================================================================

def test_revenue_growth_percentage_with_12_months(sample_validated_data_full):
    """**Validates: Requirements 2.1**
    WHEN validated GST data covering at least 12 months is received,
    THEN compute revenue_growth_percentage as ((rev_m12 - rev_m1) / rev_m1) * 100
    """
    result = _compute_revenue_growth_percentage(sample_validated_data_full)
    
    # rev_m1 = 100000, rev_m12 = 155000
    # growth = ((155000 - 100000) / 100000) * 100 = 55%
    expected = 55.0
    assert result == pytest.approx(expected, rel=0.01)


def test_revenue_growth_percentage_less_than_12_months(sample_validated_data_minimal):
    """**Validates: Requirements 2.2**
    IF GST data covers fewer than 12 months,
    THEN set revenue_growth_percentage to null
    """
    result = _compute_revenue_growth_percentage(sample_validated_data_minimal)
    assert result is None


def test_revenue_growth_percentage_zero_revenue_m1(sample_validated_data_full):
    """Test edge case where initial revenue is zero (division by zero)."""
    # Modify first month revenue to zero
    sample_validated_data_full.data.gst_data.monthly_revenue[0] = 0
    
    result = _compute_revenue_growth_percentage(sample_validated_data_full)
    assert result is None


# ============================================================================
# Test Average Monthly Balance (Requirement 2.3, 2.4)
# ============================================================================

def test_average_monthly_balance_with_6_months(sample_validated_data_full):
    """**Validates: Requirements 2.3**
    WHEN Account_Aggregator_Data covering at least 6 months is available,
    THEN compute average_monthly_balance as arithmetic mean of month-end balances
    """
    result = _compute_average_monthly_balance(sample_validated_data_full)
    
    # balances = [50000, 55000, 60000, 65000, 70000, 75000]
    # average = 375000 / 6 = 62500
    expected = 62500.0
    assert result == pytest.approx(expected, rel=0.01)


def test_average_monthly_balance_less_than_6_months(sample_validated_data_minimal):
    """**Validates: Requirements 2.4**
    IF Account_Aggregator_Data covers fewer than 6 months,
    THEN set average_monthly_balance to null
    """
    result = _compute_average_monthly_balance(sample_validated_data_minimal)
    assert result is None


# ============================================================================
# Test Cash Flow Ratio (Requirement 2.5, 2.6)
# ============================================================================

def test_cash_flow_ratio_with_6_months(sample_validated_data_full):
    """**Validates: Requirements 2.5**
    WHEN Account_Aggregator_Data covering at least 6 months is available,
    THEN compute cash_flow_ratio as (total_inflows - total_outflows) / total_inflows
    """
    result = _compute_cash_flow_ratio(sample_validated_data_full)
    
    # inflows = [200000, 210000, 220000, 230000, 240000, 250000] = 1350000
    # outflows = [150000, 155000, 160000, 165000, 170000, 175000] = 975000
    # ratio = (1350000 - 975000) / 1350000 = 375000 / 1350000 = 0.2777...
    expected = 0.2777777777777778
    assert result == pytest.approx(expected, rel=0.01)


def test_cash_flow_ratio_zero_inflows(sample_validated_data_full):
    """**Validates: Requirements 2.6**
    IF total_inflows equals zero,
    THEN set cash_flow_ratio to null
    """
    # Set all inflows to zero
    sample_validated_data_full.data.account_aggregator_data.monthly_inflows = [0, 0, 0, 0, 0, 0]
    
    result = _compute_cash_flow_ratio(sample_validated_data_full)
    assert result is None


def test_cash_flow_ratio_less_than_6_months(sample_validated_data_minimal):
    """IF Account_Aggregator_Data covers fewer than 6 months,
    THEN set cash_flow_ratio to null
    """
    result = _compute_cash_flow_ratio(sample_validated_data_minimal)
    assert result is None


# ============================================================================
# Test UPI Transaction Frequency (Requirement 2.7, 2.8)
# ============================================================================

def test_upi_transaction_frequency_with_6_months(sample_validated_data_full):
    """**Validates: Requirements 2.7**
    WHEN UPI_Data covering at least 6 months is available,
    THEN compute upi_transaction_frequency as total transaction count / number of months
    """
    result = _compute_upi_transaction_frequency(sample_validated_data_full)
    
    # 60 transactions over 590 days (first to last transaction)
    # frequency = 60 / (590/30) ≈ 3.05
    expected = 3.05
    assert result == pytest.approx(expected, rel=0.01)


def test_upi_transaction_frequency_less_than_6_months(sample_validated_data_minimal):
    """**Validates: Requirements 2.8**
    IF UPI_Data covers fewer than 6 months,
    THEN set upi_transaction_frequency to null
    """
    result = _compute_upi_transaction_frequency(sample_validated_data_minimal)
    assert result is None


def test_upi_transaction_frequency_empty_list():
    """Test edge case with no UPI transactions."""
    data = ValidatedData(
        status="VALIDATED",
        data=MSMEInput(
            gstin="29ABCDE1234F1Z5",
            pan="ABCDE1234F",
            business_registration_date=date(2022, 1, 1),
            gst_data=GSTData(
                gstin="29ABCDE1234F1Z5",
                monthly_revenue=[100000] * 12,
                filing_history=[True] * 12,
                annual_turnover=1200000,
            ),
            upi_transactions=[],
            account_aggregator_data=AccountAggregatorData(
                month_end_balances=[50000] * 6,
                monthly_inflows=[100000] * 6,
                monthly_outflows=[80000] * 6,
                statement_start_date=date(2023, 1, 1),
                statement_end_date=date(2023, 6, 30),
            ),
        ),
        data_sources_available=["GST", "AA"]
    )
    
    result = _compute_upi_transaction_frequency(data)
    assert result is None


# ============================================================================
# Test Employee Growth Percentage (Requirement 2.9, 2.10)
# ============================================================================

def test_employee_growth_percentage_with_12_months(sample_validated_data_full):
    """**Validates: Requirements 2.9**
    WHEN EPFO_Data covering at least 12 months is available,
    THEN compute employee_growth_percentage as ((emp_m12 - emp_m1) / emp_m1) * 100
    """
    result = _compute_employee_growth_percentage(sample_validated_data_full)
    
    # emp_m1 = 10, emp_m12 = 16
    # growth = ((16 - 10) / 10) * 100 = 60%
    expected = 60.0
    assert result == pytest.approx(expected, rel=0.01)


def test_employee_growth_percentage_less_than_12_months(sample_validated_data_minimal):
    """**Validates: Requirements 2.10**
    IF EPFO_Data covers fewer than 12 months,
    THEN set employee_growth_percentage to null
    """
    result = _compute_employee_growth_percentage(sample_validated_data_minimal)
    assert result is None


def test_employee_growth_percentage_zero_emp_m1(sample_validated_data_full):
    """**Validates: Requirements 2.10**
    IF employee_count_month_1 equals zero,
    THEN set employee_growth_percentage to null
    """
    # Set first month employee count to zero
    sample_validated_data_full.data.epfo_data.monthly_employee_counts[0] = 0
    
    result = _compute_employee_growth_percentage(sample_validated_data_full)
    assert result is None


def test_employee_growth_percentage_no_epfo_data(sample_validated_data_minimal):
    """Test when EPFO data is None."""
    result = _compute_employee_growth_percentage(sample_validated_data_minimal)
    assert result is None


# ============================================================================
# Test EMI to Revenue Ratio (Requirement 2.11, 2.12)
# ============================================================================

def test_emi_to_revenue_ratio_with_data(sample_validated_data_full):
    """**Validates: Requirements 2.11**
    WHEN Bank_Data covering at least 6 months is available,
    THEN compute emi_to_revenue_ratio as total_monthly_emi / average_monthly_revenue
    """
    result = _compute_emi_to_revenue_ratio(sample_validated_data_full)
    
    # monthly_emi = 30000
    # avg_monthly_revenue = sum([100000...155000]) / 12 = 1530000 / 12 = 127500
    # ratio = 30000 / 127500 = 0.2353...
    expected = 0.23529411764705882
    assert result == pytest.approx(expected, rel=0.01)


def test_emi_to_revenue_ratio_zero_revenue(sample_validated_data_full):
    """**Validates: Requirements 2.12**
    IF average_monthly_revenue equals zero,
    THEN set emi_to_revenue_ratio to null
    """
    # Set all revenue to zero
    sample_validated_data_full.data.gst_data.monthly_revenue = [0] * 12
    
    result = _compute_emi_to_revenue_ratio(sample_validated_data_full)
    assert result is None


def test_emi_to_revenue_ratio_no_bank_data(sample_validated_data_minimal):
    """Test when Bank data is None."""
    result = _compute_emi_to_revenue_ratio(sample_validated_data_minimal)
    assert result is None


# ============================================================================
# Test Business Age Months (Requirement 2.13)
# ============================================================================

def test_business_age_months_calculation(sample_validated_data_full):
    """**Validates: Requirements 2.13**
    WHEN business registration date is available,
    THEN compute business_age_months as number of complete months between
    registration date and current date
    """
    result = _compute_business_age_months(sample_validated_data_full)
    
    # Registration date: 2022-01-01
    # Current date: varies, but should be at least 24 months (2 years)
    assert result is not None
    assert result >= 0
    # Since registration was Jan 2022 and we're in 2024+, should be at least 24 months
    assert result >= 24


def test_business_age_months_recent_registration(sample_validated_data_minimal):
    """Test with recent registration date."""
    result = _compute_business_age_months(sample_validated_data_minimal)
    
    # Registration date: 2023-10-01
    # Should be at least a few months old
    assert result is not None
    assert result >= 0


# ============================================================================
# Test Digital Payment Ratio (Requirement 2.14, 2.15)
# ============================================================================

def test_digital_payment_ratio_with_data(sample_validated_data_full):
    """**Validates: Requirements 2.14**
    WHEN UPI_Data covering at least 6 months and total_revenue are available,
    THEN compute digital_payment_ratio as total_upi_volume / total_revenue
    """
    result = _compute_digital_payment_ratio(sample_validated_data_full)
    
    # total_upi_volume = 60 transactions * 1000.50 = 60030
    # total_revenue = sum([100000...155000]) = 1530000
    # ratio = 60030 / 1530000 = 0.0392...
    expected = 0.03923529411764706
    assert result == pytest.approx(expected, rel=0.01)


def test_digital_payment_ratio_zero_revenue(sample_validated_data_full):
    """**Validates: Requirements 2.15**
    IF total_revenue equals zero,
    THEN set digital_payment_ratio to null
    """
    # Set all revenue to zero
    sample_validated_data_full.data.gst_data.monthly_revenue = [0] * 12
    
    result = _compute_digital_payment_ratio(sample_validated_data_full)
    assert result is None


def test_digital_payment_ratio_less_than_6_months(sample_validated_data_minimal):
    """IF UPI_Data covers fewer than 6 months,
    THEN set digital_payment_ratio to null
    """
    result = _compute_digital_payment_ratio(sample_validated_data_minimal)
    assert result is None


# ============================================================================
# Test Normalization (Requirement 2.16, 2.17)
# ============================================================================

def test_normalize_valid_value():
    """**Validates: Requirements 2.16**
    WHEN at least one numeric feature has a non-null value,
    THEN normalize each non-null numeric feature to range [0, 1] using min-max scaling
    """
    # Test with revenue_growth_percentage: [-100, 500]
    # value = 200, min = -100, max = 500
    # normalized = (200 - (-100)) / (500 - (-100)) = 300 / 600 = 0.5
    result = _normalize(200.0, 'revenue_growth_percentage')
    assert result == pytest.approx(0.5, rel=0.001)


def test_normalize_min_value():
    """Test normalization at minimum bound."""
    # Test with cash_flow_ratio: [-1, 1]
    # value = -1 (min)
    # normalized = (-1 - (-1)) / (1 - (-1)) = 0 / 2 = 0.0
    result = _normalize(-1.0, 'cash_flow_ratio')
    assert result == pytest.approx(0.0, rel=0.001)


def test_normalize_max_value():
    """Test normalization at maximum bound."""
    # Test with cash_flow_ratio: [-1, 1]
    # value = 1 (max)
    # normalized = (1 - (-1)) / (1 - (-1)) = 2 / 2 = 1.0
    result = _normalize(1.0, 'cash_flow_ratio')
    assert result == pytest.approx(1.0, rel=0.001)


def test_normalize_null_value():
    """**Validates: Requirements 2.18**
    WHEN feature engineering completes,
    THEN null values are represented as -1
    """
    result = _normalize(None, 'revenue_growth_percentage')
    assert result == -1.0


def test_normalize_equal_min_max():
    """**Validates: Requirements 2.17**
    IF a numeric feature has only one unique non-null value across training data,
    THEN set the normalized value to 0.5
    """
    # Simulate this by temporarily modifying normalization bounds
    from agents.risk_intelligence_agent import feature_engineering
    
    # Save original bounds
    original_bounds = feature_engineering._NORMALIZATION_BOUNDS.copy()
    
    # Set equal min and max
    feature_engineering._NORMALIZATION_BOUNDS['test_feature'] = (100.0, 100.0)
    
    result = _normalize(100.0, 'test_feature')
    assert result == 0.5
    
    # Restore original bounds
    feature_engineering._NORMALIZATION_BOUNDS = original_bounds


def test_normalize_outside_bounds_clamped():
    """Test that values outside training bounds are clamped to [0, 1]."""
    # Test with value above max
    # revenue_growth_percentage: [-100, 500]
    # value = 600 (above max)
    result = _normalize(600.0, 'revenue_growth_percentage')
    assert result == 1.0  # Clamped to max
    
    # Test with value below min
    # value = -200 (below min)
    result = _normalize(-200.0, 'revenue_growth_percentage')
    assert result == 0.0  # Clamped to min


# ============================================================================
# Test Feature Vector Output (Requirement 2.18)
# ============================================================================

def test_engineer_features_returns_8_elements(sample_validated_data_full):
    """**Validates: Requirements 2.18**
    WHEN feature engineering completes,
    THEN return feature vector as numeric array containing exactly 8 elements
    """
    result = engineer_features(sample_validated_data_full)
    
    assert isinstance(result, FeatureVector)
    assert len(result.values) == 8
    assert len(result.feature_names) == 8
    assert len(result.null_flags) == 8


def test_engineer_features_correct_order(sample_validated_data_full):
    """**Validates: Requirements 2.18**
    Verify features are in correct order:
    0: revenue_growth_percentage
    1: average_monthly_balance
    2: cash_flow_ratio
    3: upi_transaction_frequency
    4: employee_growth_percentage
    5: emi_to_revenue_ratio
    6: business_age_months
    7: digital_payment_ratio
    """
    result = engineer_features(sample_validated_data_full)
    
    expected_order = [
        'revenue_growth_percentage',
        'average_monthly_balance',
        'cash_flow_ratio',
        'upi_transaction_frequency',
        'employee_growth_percentage',
        'emi_to_revenue_ratio',
        'business_age_months',
        'digital_payment_ratio',
    ]
    
    assert result.feature_names == expected_order


def test_engineer_features_null_values_as_minus_one(sample_validated_data_minimal):
    """**Validates: Requirements 2.18**
    WHEN feature engineering completes,
    THEN null values are represented as -1
    """
    result = engineer_features(sample_validated_data_minimal)
    
    # With minimal data, many features should be null (encoded as -1)
    # revenue_growth_percentage: null (< 12 months) -> -1
    # average_monthly_balance: null (< 6 months) -> -1
    # cash_flow_ratio: null (< 6 months) -> -1
    # upi_transaction_frequency: null (< 6 months) -> -1
    # employee_growth_percentage: null (no EPFO data) -> -1
    # emi_to_revenue_ratio: null (no bank data) -> -1
    # business_age_months: should have value
    # digital_payment_ratio: null (< 6 months UPI) -> -1
    
    assert result.values[0] == -1.0  # revenue_growth_percentage
    assert result.values[1] == -1.0  # average_monthly_balance
    assert result.values[2] == -1.0  # cash_flow_ratio
    assert result.values[3] == -1.0  # upi_transaction_frequency
    assert result.values[4] == -1.0  # employee_growth_percentage
    assert result.values[5] == -1.0  # emi_to_revenue_ratio
    assert result.values[6] >= 0.0   # business_age_months (should have value)
    assert result.values[7] == -1.0  # digital_payment_ratio


def test_engineer_features_null_flags_correct(sample_validated_data_minimal):
    """Test that null_flags correctly indicate which features were null."""
    result = engineer_features(sample_validated_data_minimal)
    
    # Verify null_flags match the -1 values
    for i, (value, is_null) in enumerate(zip(result.values, result.null_flags)):
        if is_null:
            assert value == -1.0, f"Feature {i} marked as null but value is {value}"
        else:
            assert value != -1.0, f"Feature {i} not marked as null but value is -1.0"


def test_engineer_features_all_values_normalized(sample_validated_data_full):
    """Test that all non-null values are properly normalized to [0, 1] range."""
    result = engineer_features(sample_validated_data_full)
    
    for i, (value, is_null) in enumerate(zip(result.values, result.null_flags)):
        if not is_null:
            assert 0.0 <= value <= 1.0, f"Feature {i} value {value} not in [0, 1] range"


def test_engineer_features_no_none_or_nan(sample_validated_data_full):
    """**Validates: Requirements 2.18**
    Ensure feature vector never contains None or NaN, only -1 for null values.
    """
    result = engineer_features(sample_validated_data_full)
    
    for i, value in enumerate(result.values):
        assert value is not None, f"Feature {i} is None"
        assert not (isinstance(value, float) and value != value), f"Feature {i} is NaN"


# ============================================================================
# Integration Tests
# ============================================================================

def test_full_feature_engineering_pipeline_complete_data(sample_validated_data_full):
    """Integration test with complete data - all features should be computed."""
    result = engineer_features(sample_validated_data_full)
    
    # All features should have values (not null)
    assert all(not flag for flag in result.null_flags), "Some features are null with complete data"
    
    # All values should be in [0, 1] range
    assert all(0.0 <= value <= 1.0 for value in result.values)
    
    # Verify specific computed values
    assert result.values[0] >= 0.0  # revenue_growth_percentage (positive growth)
    assert result.values[1] >= 0.0  # average_monthly_balance (positive balance)
    assert result.values[2] >= 0.0  # cash_flow_ratio (positive cash flow)
    assert result.values[3] >= 0.0  # upi_transaction_frequency (has transactions)
    assert result.values[4] >= 0.0  # employee_growth_percentage (positive growth)
    assert result.values[5] >= 0.0  # emi_to_revenue_ratio (has EMI)
    assert result.values[6] >= 0.0  # business_age_months (has age)
    assert result.values[7] >= 0.0  # digital_payment_ratio (has UPI)


def test_full_feature_engineering_pipeline_minimal_data(sample_validated_data_minimal):
    """Integration test with minimal data - most features should be null."""
    result = engineer_features(sample_validated_data_minimal)
    
    # Most features should be null except business_age_months
    null_count = sum(result.null_flags)
    assert null_count >= 6, f"Expected at least 6 null features, got {null_count}"
    
    # business_age_months should have a value
    business_age_idx = 6
    assert not result.null_flags[business_age_idx]
    assert result.values[business_age_idx] >= 0.0


def test_edge_case_negative_growth():
    """Test handling of negative revenue growth."""
    data = ValidatedData(
        status="VALIDATED",
        data=MSMEInput(
            gstin="29ABCDE1234F1Z5",
            pan="ABCDE1234F",
            business_registration_date=date(2022, 1, 1),
            gst_data=GSTData(
                gstin="29ABCDE1234F1Z5",
                monthly_revenue=[200000, 190000, 180000, 170000, 160000, 150000,
                               140000, 130000, 120000, 110000, 100000, 90000],  # Declining
                filing_history=[True] * 12,
                annual_turnover=1800000,
            ),
            upi_transactions=[
                UPITransaction(
                    amount=1000.0,
                    timestamp=datetime(2023, 1, 1) + timedelta(days=i * 10),
                    counterparty=f"customer_{i}"
                )
                for i in range(60)
            ],
            account_aggregator_data=AccountAggregatorData(
                month_end_balances=[50000] * 6,
                monthly_inflows=[100000] * 6,
                monthly_outflows=[80000] * 6,
                statement_start_date=date(2023, 1, 1),
                statement_end_date=date(2023, 6, 30),
            ),
        ),
        data_sources_available=["GST", "UPI", "AA"]
    )
    
    result = _compute_revenue_growth_percentage(data)
    
    # rev_m1 = 200000, rev_m12 = 90000
    # growth = ((90000 - 200000) / 200000) * 100 = -55%
    expected = -55.0
    assert result == pytest.approx(expected, rel=0.01)


def test_edge_case_negative_cash_flow():
    """Test handling of negative cash flow (outflows > inflows)."""
    data = ValidatedData(
        status="VALIDATED",
        data=MSMEInput(
            gstin="29ABCDE1234F1Z5",
            pan="ABCDE1234F",
            business_registration_date=date(2022, 1, 1),
            gst_data=GSTData(
                gstin="29ABCDE1234F1Z5",
                monthly_revenue=[100000] * 12,
                filing_history=[True] * 12,
                annual_turnover=1200000,
            ),
            upi_transactions=[],
            account_aggregator_data=AccountAggregatorData(
                month_end_balances=[50000] * 6,
                monthly_inflows=[100000] * 6,
                monthly_outflows=[150000] * 6,  # More outflows than inflows
                statement_start_date=date(2023, 1, 1),
                statement_end_date=date(2023, 6, 30),
            ),
        ),
        data_sources_available=["GST", "AA"]
    )
    
    result = _compute_cash_flow_ratio(data)
    
    # inflows = 600000, outflows = 900000
    # ratio = (600000 - 900000) / 600000 = -0.5
    expected = -0.5
    assert result == pytest.approx(expected, rel=0.01)


# ============================================================================
# Additional Unit Tests for Task 4.3 Requirements
# ============================================================================

def test_revenue_growth_with_exact_12_months():
    """**Validates: Requirements 2.2**
    Test revenue growth computation with exact 12-month data.
    Ensure it handles exactly 12 months (not more, not less).
    """
    data = ValidatedData(
        status="VALIDATED",
        data=MSMEInput(
            gstin="29ABCDE1234F1Z5",
            pan="ABCDE1234F",
            business_registration_date=date(2022, 1, 1),
            gst_data=GSTData(
                gstin="29ABCDE1234F1Z5",
                # Exactly 12 months: 100k to 150k (50% growth)
                monthly_revenue=[100000, 105000, 110000, 115000, 120000, 125000,
                               130000, 135000, 140000, 145000, 150000, 155000],
                filing_history=[True] * 12,
                annual_turnover=1500000,
            ),
            upi_transactions=[],
            account_aggregator_data=AccountAggregatorData(
                month_end_balances=[50000] * 6,
                monthly_inflows=[100000] * 6,
                monthly_outflows=[80000] * 6,
                statement_start_date=date(2023, 1, 1),
                statement_end_date=date(2023, 6, 30),
            ),
        ),
        data_sources_available=["GST", "AA"]
    )
    
    result = _compute_revenue_growth_percentage(data)
    
    # Formula: ((rev_m12 - rev_m1) / rev_m1) * 100
    # (155000 - 100000) / 100000 * 100 = 55%
    assert result is not None
    assert result == pytest.approx(55.0, rel=0.001)


def test_cash_flow_ratio_with_zero_inflows_returns_null():
    """**Validates: Requirements 2.6**
    Test that cash flow ratio returns null when total inflows are zero.
    This is a critical division-by-zero case.
    """
    data = ValidatedData(
        status="VALIDATED",
        data=MSMEInput(
            gstin="29ABCDE1234F1Z5",
            pan="ABCDE1234F",
            business_registration_date=date(2022, 1, 1),
            gst_data=GSTData(
                gstin="29ABCDE1234F1Z5",
                monthly_revenue=[100000] * 12,
                filing_history=[True] * 12,
                annual_turnover=1200000,
            ),
            upi_transactions=[],
            account_aggregator_data=AccountAggregatorData(
                month_end_balances=[50000] * 6,
                monthly_inflows=[0, 0, 0, 0, 0, 0],  # Zero inflows
                monthly_outflows=[10000, 10000, 10000, 10000, 10000, 10000],
                statement_start_date=date(2023, 1, 1),
                statement_end_date=date(2023, 6, 30),
            ),
        ),
        data_sources_available=["GST", "AA"]
    )
    
    result = _compute_cash_flow_ratio(data)
    assert result is None, "Cash flow ratio should be None when inflows are zero"


def test_division_by_zero_emi_to_revenue_ratio():
    """**Validates: Requirements 2.12**
    Test EMI to revenue ratio with zero average revenue.
    """
    data = ValidatedData(
        status="VALIDATED",
        data=MSMEInput(
            gstin="29ABCDE1234F1Z5",
            pan="ABCDE1234F",
            business_registration_date=date(2022, 1, 1),
            gst_data=GSTData(
                gstin="29ABCDE1234F1Z5",
                monthly_revenue=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # All zero
                filing_history=[True] * 12,
                annual_turnover=0,
            ),
            upi_transactions=[],
            account_aggregator_data=AccountAggregatorData(
                month_end_balances=[50000] * 6,
                monthly_inflows=[100000] * 6,
                monthly_outflows=[80000] * 6,
                statement_start_date=date(2023, 1, 1),
                statement_end_date=date(2023, 6, 30),
            ),
            bank_data=BankData(
                total_monthly_emi=30000,
                loan_amounts=[500000],
                account_number="1234567890",
            ),
        ),
        data_sources_available=["GST", "AA", "BANK"]
    )
    
    result = _compute_emi_to_revenue_ratio(data)
    assert result is None, "EMI to revenue ratio should be None when average revenue is zero"


def test_division_by_zero_digital_payment_ratio():
    """**Validates: Requirements 2.15**
    Test digital payment ratio with zero total revenue.
    """
    data = ValidatedData(
        status="VALIDATED",
        data=MSMEInput(
            gstin="29ABCDE1234F1Z5",
            pan="ABCDE1234F",
            business_registration_date=date(2022, 1, 1),
            gst_data=GSTData(
                gstin="29ABCDE1234F1Z5",
                monthly_revenue=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # All zero
                filing_history=[True] * 12,
                annual_turnover=0,
            ),
            upi_transactions=[
                UPITransaction(
                    amount=1000.50,
                    timestamp=datetime(2023, 1, 1) + timedelta(days=i * 10),
                    counterparty=f"customer_{i}"
                )
                for i in range(60)  # 600 days of UPI data
            ],
            account_aggregator_data=AccountAggregatorData(
                month_end_balances=[50000] * 6,
                monthly_inflows=[100000] * 6,
                monthly_outflows=[80000] * 6,
                statement_start_date=date(2023, 1, 1),
                statement_end_date=date(2023, 6, 30),
            ),
        ),
        data_sources_available=["GST", "UPI", "AA"]
    )
    
    result = _compute_digital_payment_ratio(data)
    assert result is None, "Digital payment ratio should be None when total revenue is zero"


def test_division_by_zero_revenue_growth_with_zero_initial():
    """**Validates: Requirements 2.2**
    Test revenue growth with zero initial revenue (month 1).
    """
    data = ValidatedData(
        status="VALIDATED",
        data=MSMEInput(
            gstin="29ABCDE1234F1Z5",
            pan="ABCDE1234F",
            business_registration_date=date(2022, 1, 1),
            gst_data=GSTData(
                gstin="29ABCDE1234F1Z5",
                monthly_revenue=[0, 100000, 110000, 120000, 130000, 140000,
                               150000, 160000, 170000, 180000, 190000, 200000],  # First month is zero
                filing_history=[True] * 12,
                annual_turnover=1500000,
            ),
            upi_transactions=[],
            account_aggregator_data=AccountAggregatorData(
                month_end_balances=[50000] * 6,
                monthly_inflows=[100000] * 6,
                monthly_outflows=[80000] * 6,
                statement_start_date=date(2023, 1, 1),
                statement_end_date=date(2023, 6, 30),
            ),
        ),
        data_sources_available=["GST", "AA"]
    )
    
    result = _compute_revenue_growth_percentage(data)
    assert result is None, "Revenue growth should be None when initial revenue is zero"


def test_division_by_zero_employee_growth_with_zero_initial():
    """**Validates: Requirements 2.10**
    Test employee growth with zero initial employee count.
    """
    data = ValidatedData(
        status="VALIDATED",
        data=MSMEInput(
            gstin="29ABCDE1234F1Z5",
            pan="ABCDE1234F",
            business_registration_date=date(2022, 1, 1),
            gst_data=GSTData(
                gstin="29ABCDE1234F1Z5",
                monthly_revenue=[100000] * 12,
                filing_history=[True] * 12,
                annual_turnover=1200000,
            ),
            upi_transactions=[],
            account_aggregator_data=AccountAggregatorData(
                month_end_balances=[50000] * 6,
                monthly_inflows=[100000] * 6,
                monthly_outflows=[80000] * 6,
                statement_start_date=date(2023, 1, 1),
                statement_end_date=date(2023, 6, 30),
            ),
            epfo_data=EPFOData(
                monthly_employee_counts=[0, 5, 8, 10, 12, 14, 15, 16, 17, 18, 19, 20]  # First month is zero
            ),
        ),
        data_sources_available=["GST", "AA", "EPFO"]
    )
    
    result = _compute_employee_growth_percentage(data)
    assert result is None, "Employee growth should be None when initial employee count is zero"


def test_min_max_normalization_single_unique_value():
    """**Validates: Requirements 2.17**
    Test min-max normalization when min equals max (single unique value).
    Should return 0.5 as specified.
    """
    from agents.risk_intelligence_agent import feature_engineering
    
    # Save original bounds
    original_bounds = feature_engineering._NORMALIZATION_BOUNDS.copy()
    
    try:
        # Create a feature with equal min and max
        feature_engineering._NORMALIZATION_BOUNDS['test_single_value'] = (100.0, 100.0)
        
        result = _normalize(100.0, 'test_single_value')
        assert result == 0.5, "Normalization with min==max should return 0.5"
        
        # Test with a different value (should still be 0.5)
        result2 = _normalize(50.0, 'test_single_value')
        assert result2 == 0.5, "Any value should normalize to 0.5 when min==max"
        
        result3 = _normalize(150.0, 'test_single_value')
        assert result3 == 0.5, "Any value should normalize to 0.5 when min==max"
        
    finally:
        # Restore original bounds
        feature_engineering._NORMALIZATION_BOUNDS = original_bounds


def test_insufficient_time_series_data_revenue_growth():
    """**Validates: Requirements 2.2**
    Test insufficient time-series data handling for revenue growth.
    """
    # Test with 11 months (insufficient)
    data = ValidatedData(
        status="VALIDATED",
        data=MSMEInput(
            gstin="29ABCDE1234F1Z5",
            pan="ABCDE1234F",
            business_registration_date=date(2022, 1, 1),
            gst_data=GSTData(
                gstin="29ABCDE1234F1Z5",
                monthly_revenue=[100000, 105000, 110000, 115000, 120000, 125000,
                               130000, 135000, 140000, 145000, 150000],  # 11 months
                filing_history=[True] * 11,
                annual_turnover=1400000,
            ),
            upi_transactions=[],
            account_aggregator_data=AccountAggregatorData(
                month_end_balances=[50000] * 6,
                monthly_inflows=[100000] * 6,
                monthly_outflows=[80000] * 6,
                statement_start_date=date(2023, 1, 1),
                statement_end_date=date(2023, 6, 30),
            ),
        ),
        data_sources_available=["GST", "AA"]
    )
    
    result = _compute_revenue_growth_percentage(data)
    assert result is None, "Revenue growth should be None with < 12 months of data"


def test_insufficient_time_series_data_average_balance():
    """**Validates: Requirements 2.4**
    Test insufficient time-series data handling for average balance.
    """
    # Test with 5 months (insufficient)
    data = ValidatedData(
        status="VALIDATED",
        data=MSMEInput(
            gstin="29ABCDE1234F1Z5",
            pan="ABCDE1234F",
            business_registration_date=date(2022, 1, 1),
            gst_data=GSTData(
                gstin="29ABCDE1234F1Z5",
                monthly_revenue=[100000] * 12,
                filing_history=[True] * 12,
                annual_turnover=1200000,
            ),
            upi_transactions=[],
            account_aggregator_data=AccountAggregatorData(
                month_end_balances=[50000, 55000, 60000, 65000, 70000],  # 5 months
                monthly_inflows=[100000, 105000, 110000, 115000, 120000],
                monthly_outflows=[80000, 85000, 90000, 95000, 100000],
                statement_start_date=date(2023, 1, 1),
                statement_end_date=date(2023, 5, 31),
            ),
        ),
        data_sources_available=["GST", "AA"]
    )
    
    result = _compute_average_monthly_balance(data)
    assert result is None, "Average monthly balance should be None with < 6 months of data"


def test_insufficient_time_series_data_cash_flow():
    """**Validates: Requirements 2.6**
    Test insufficient time-series data handling for cash flow ratio.
    """
    # Test with 5 months (insufficient)
    data = ValidatedData(
        status="VALIDATED",
        data=MSMEInput(
            gstin="29ABCDE1234F1Z5",
            pan="ABCDE1234F",
            business_registration_date=date(2022, 1, 1),
            gst_data=GSTData(
                gstin="29ABCDE1234F1Z5",
                monthly_revenue=[100000] * 12,
                filing_history=[True] * 12,
                annual_turnover=1200000,
            ),
            upi_transactions=[],
            account_aggregator_data=AccountAggregatorData(
                month_end_balances=[50000, 55000, 60000, 65000, 70000],  # 5 months
                monthly_inflows=[100000, 105000, 110000, 115000, 120000],
                monthly_outflows=[80000, 85000, 90000, 95000, 100000],
                statement_start_date=date(2023, 1, 1),
                statement_end_date=date(2023, 5, 31),
            ),
        ),
        data_sources_available=["GST", "AA"]
    )
    
    result = _compute_cash_flow_ratio(data)
    assert result is None, "Cash flow ratio should be None with < 6 months of data"


def test_insufficient_time_series_data_upi_frequency():
    """**Validates: Requirements 2.8**
    Test insufficient time-series data handling for UPI transaction frequency.
    """
    # Test with less than 6 months (179 days)
    data = ValidatedData(
        status="VALIDATED",
        data=MSMEInput(
            gstin="29ABCDE1234F1Z5",
            pan="ABCDE1234F",
            business_registration_date=date(2022, 1, 1),
            gst_data=GSTData(
                gstin="29ABCDE1234F1Z5",
                monthly_revenue=[100000] * 12,
                filing_history=[True] * 12,
                annual_turnover=1200000,
            ),
            upi_transactions=[
                UPITransaction(
                    amount=1000.50,
                    timestamp=datetime(2023, 1, 1) + timedelta(days=i * 5),
                    counterparty=f"customer_{i}"
                )
                for i in range(30)  # 30 transactions over 145 days (< 180)
            ],
            account_aggregator_data=AccountAggregatorData(
                month_end_balances=[50000] * 6,
                monthly_inflows=[100000] * 6,
                monthly_outflows=[80000] * 6,
                statement_start_date=date(2023, 1, 1),
                statement_end_date=date(2023, 6, 30),
            ),
        ),
        data_sources_available=["GST", "UPI", "AA"]
    )
    
    result = _compute_upi_transaction_frequency(data)
    assert result is None, "UPI transaction frequency should be None with < 6 months (180 days) of data"


def test_insufficient_time_series_data_employee_growth():
    """**Validates: Requirements 2.10**
    Test insufficient time-series data handling for employee growth.
    """
    # Test with 11 months (insufficient)
    data = ValidatedData(
        status="VALIDATED",
        data=MSMEInput(
            gstin="29ABCDE1234F1Z5",
            pan="ABCDE1234F",
            business_registration_date=date(2022, 1, 1),
            gst_data=GSTData(
                gstin="29ABCDE1234F1Z5",
                monthly_revenue=[100000] * 12,
                filing_history=[True] * 12,
                annual_turnover=1200000,
            ),
            upi_transactions=[],
            account_aggregator_data=AccountAggregatorData(
                month_end_balances=[50000] * 6,
                monthly_inflows=[100000] * 6,
                monthly_outflows=[80000] * 6,
                statement_start_date=date(2023, 1, 1),
                statement_end_date=date(2023, 6, 30),
            ),
            epfo_data=EPFOData(
                monthly_employee_counts=[10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]  # 11 months
            ),
        ),
        data_sources_available=["GST", "AA", "EPFO"]
    )
    
    result = _compute_employee_growth_percentage(data)
    assert result is None, "Employee growth should be None with < 12 months of data"


def test_feature_vector_all_division_by_zero_cases():
    """**Validates: Requirements 2.6, 2.10, 2.12, 2.15, 2.17**
    Integration test verifying all division-by-zero cases are handled correctly.
    """
    data = ValidatedData(
        status="VALIDATED",
        data=MSMEInput(
            gstin="29ABCDE1234F1Z5",
            pan="ABCDE1234F",
            business_registration_date=date(2022, 1, 1),
            gst_data=GSTData(
                gstin="29ABCDE1234F1Z5",
                monthly_revenue=[0] * 12,  # Zero revenue -> affects emi_to_revenue and digital_payment
                filing_history=[True] * 12,
                annual_turnover=0,
            ),
            upi_transactions=[
                UPITransaction(
                    amount=1000.50,
                    timestamp=datetime(2023, 1, 1) + timedelta(days=i * 10),
                    counterparty=f"customer_{i}"
                )
                for i in range(60)
            ],
            account_aggregator_data=AccountAggregatorData(
                month_end_balances=[50000] * 6,
                monthly_inflows=[0, 0, 0, 0, 0, 0],  # Zero inflows -> affects cash_flow_ratio
                monthly_outflows=[10000] * 6,
                statement_start_date=date(2023, 1, 1),
                statement_end_date=date(2023, 6, 30),
            ),
            epfo_data=EPFOData(
                monthly_employee_counts=[0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]  # Zero initial -> affects employee_growth
            ),
            bank_data=BankData(
                total_monthly_emi=30000,
                loan_amounts=[500000],
                account_number="1234567890",
            ),
        ),
        data_sources_available=["GST", "UPI", "AA", "EPFO", "BANK"]
    )
    
    result = engineer_features(data)
    
    # Check that all affected features are -1 (null)
    # revenue_growth_percentage: null due to zero initial revenue
    assert result.values[0] == -1.0
    # cash_flow_ratio: null due to zero inflows
    assert result.values[2] == -1.0
    # employee_growth_percentage: null due to zero initial employees
    assert result.values[4] == -1.0
    # emi_to_revenue_ratio: null due to zero revenue
    assert result.values[5] == -1.0
    # digital_payment_ratio: null due to zero revenue
    assert result.values[7] == -1.0


# ============================================================================
# Property-Based Tests
# ============================================================================

from hypothesis import given, strategies as st, assume
from hypothesis.strategies import composite
import math


@composite
def valid_validated_data(draw):
    """Generate random ValidatedData with varying data completeness for PBT.
    
    This strategy creates ValidatedData instances with:
    - Varying amounts of historical data (0-24 months)
    - Optional EPFO and Bank data
    - Random but valid values for all fields
    """
    # Generate random months of data (0-24)
    gst_months = draw(st.integers(min_value=0, max_value=24))
    aa_months = draw(st.integers(min_value=0, max_value=24))
    upi_days_span = draw(st.integers(min_value=0, max_value=730))  # 0-2 years
    epfo_months = draw(st.integers(min_value=0, max_value=24))
    
    # Generate optional data flags
    has_epfo = draw(st.booleans())
    has_bank = draw(st.booleans())
    
    # Generate GST data
    monthly_revenue = [
        draw(st.floats(min_value=0, max_value=10000000, allow_nan=False, allow_infinity=False))
        for _ in range(gst_months)
    ]
    filing_history = [draw(st.booleans()) for _ in range(gst_months)]
    annual_turnover = draw(st.floats(min_value=0, max_value=100000000, allow_nan=False, allow_infinity=False))
    
    # Generate UPI transactions
    if upi_days_span > 0:
        num_transactions = draw(st.integers(min_value=1, max_value=100))
        base_timestamp = datetime(2023, 1, 1)
        upi_transactions = [
            UPITransaction(
                amount=round(draw(st.floats(min_value=0.01, max_value=1000000, allow_nan=False, allow_infinity=False)), 2),
                timestamp=base_timestamp + timedelta(days=draw(st.integers(min_value=0, max_value=upi_days_span))),
                counterparty=f"counterparty_{i}"
            )
            for i in range(num_transactions)
        ]
    else:
        upi_transactions = [
            UPITransaction(
                amount=100.50,
                timestamp=datetime(2023, 1, 1),
                counterparty="test"
            )
        ]
    
    # Generate Account Aggregator data
    month_end_balances = [
        draw(st.floats(min_value=0, max_value=10000000, allow_nan=False, allow_infinity=False))
        for _ in range(aa_months)
    ]
    monthly_inflows = [
        draw(st.floats(min_value=0, max_value=10000000, allow_nan=False, allow_infinity=False))
        for _ in range(aa_months)
    ]
    monthly_outflows = [
        draw(st.floats(min_value=0, max_value=10000000, allow_nan=False, allow_infinity=False))
        for _ in range(aa_months)
    ]
    
    # Generate dates ensuring at least 90 days span
    statement_start = date(2023, 1, 1)
    statement_end = statement_start + timedelta(days=90)
    
    # Generate EPFO data if enabled
    epfo_data = None
    if has_epfo:
        epfo_data = EPFOData(
            monthly_employee_counts=[
                draw(st.integers(min_value=0, max_value=1000))
                for _ in range(epfo_months)
            ]
        )
    
    # Generate Bank data if enabled
    bank_data = None
    if has_bank:
        bank_data = BankData(
            total_monthly_emi=draw(st.floats(min_value=0, max_value=1000000, allow_nan=False, allow_infinity=False)),
            loan_amounts=[draw(st.floats(min_value=0, max_value=10000000, allow_nan=False, allow_infinity=False))],
            account_number=f"ACC{draw(st.integers(min_value=1000000000, max_value=9999999999))}"
        )
    
    # Generate registration date
    reg_date = date(2020, 1, 1) + timedelta(days=draw(st.integers(min_value=0, max_value=1460)))
    
    # Build ValidatedData
    data = ValidatedData(
        status="VALIDATED",
        data=MSMEInput(
            gstin="29ABCDE1234F1Z5",
            pan="ABCDE1234F",
            business_registration_date=reg_date,
            gst_data=GSTData(
                gstin="29ABCDE1234F1Z5",
                monthly_revenue=monthly_revenue if gst_months > 0 else [100000],
                filing_history=filing_history if gst_months > 0 else [True],
                annual_turnover=annual_turnover,
            ),
            upi_transactions=upi_transactions,
            account_aggregator_data=AccountAggregatorData(
                month_end_balances=month_end_balances if aa_months > 0 else [50000],
                monthly_inflows=monthly_inflows if aa_months > 0 else [100000],
                monthly_outflows=monthly_outflows if aa_months > 0 else [80000],
                statement_start_date=statement_start,
                statement_end_date=statement_end,
            ),
            epfo_data=epfo_data,
            bank_data=bank_data,
        ),
        data_sources_available=["GST", "UPI", "AA"] + (["EPFO"] if has_epfo else []) + (["BANK"] if has_bank else [])
    )
    
    return data


@given(data=valid_validated_data())
def test_property_feature_vector_length_invariant(data):
    """**Property 3: Feature Vector Length Invariant**
    **Validates: Requirements 2.18**
    
    For ANY valid input with varying data completeness:
    - Output ALWAYS has exactly 8 elements
    - Null features are ALWAYS encoded as -1.0, NEVER None or NaN
    - Feature vector values are ALWAYS in [-1, 1] range
    
    This property holds regardless of:
    - How many months of data are available
    - Which optional data sources (EPFO, Bank) are present
    - The specific values in the data
    """
    # Execute feature engineering
    result = engineer_features(data)
    
    # Property 1: Feature vector ALWAYS has exactly 8 elements
    assert len(result.values) == 8, f"Feature vector must have exactly 8 elements, got {len(result.values)}"
    assert len(result.feature_names) == 8, f"Feature names must have exactly 8 elements, got {len(result.feature_names)}"
    assert len(result.null_flags) == 8, f"Null flags must have exactly 8 elements, got {len(result.null_flags)}"
    
    # Property 2: Null features are ALWAYS encoded as -1.0, NEVER None or NaN
    for i, value in enumerate(result.values):
        # Must never be None
        assert value is not None, f"Feature {i} ({result.feature_names[i]}) is None, should be -1.0 for null"
        
        # Must never be NaN
        assert not math.isnan(value), f"Feature {i} ({result.feature_names[i]}) is NaN, should be -1.0 for null"
        
        # Must never be infinity
        assert not math.isinf(value), f"Feature {i} ({result.feature_names[i]}) is infinity"
    
    # Property 3: Feature vector values are ALWAYS in [-1, 1] range
    for i, (value, is_null) in enumerate(zip(result.values, result.null_flags)):
        if is_null:
            # Null features MUST be exactly -1.0
            assert value == -1.0, f"Feature {i} ({result.feature_names[i]}) marked as null but value is {value}, should be -1.0"
        else:
            # Non-null features MUST be in [0, 1] range (normalized)
            assert 0.0 <= value <= 1.0, f"Feature {i} ({result.feature_names[i]}) value {value} not in [0, 1] range"
    
    # Property 4: Consistency between null_flags and -1.0 encoding
    for i, (value, is_null) in enumerate(zip(result.values, result.null_flags)):
        if value == -1.0:
            assert is_null, f"Feature {i} ({result.feature_names[i]}) has value -1.0 but null_flag is False"
        if is_null:
            assert value == -1.0, f"Feature {i} ({result.feature_names[i]}) has null_flag True but value is {value}"
    
    # Property 5: Feature names are in the specified order
    expected_order = [
        'revenue_growth_percentage',
        'average_monthly_balance',
        'cash_flow_ratio',
        'upi_transaction_frequency',
        'employee_growth_percentage',
        'emi_to_revenue_ratio',
        'business_age_months',
        'digital_payment_ratio',
    ]
    assert result.feature_names == expected_order, f"Feature names not in expected order"
