"""Property-based tests for Validator using Hypothesis.

Validates Property: Feature Vector Length Invariant / validator robustness.
Requirements: 1.1, 1.7
"""

import pytest
import sys
from pathlib import Path
from hypothesis import given, strategies as st, settings, HealthCheck

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.risk_intelligence_agent.validator import validate
from agents.risk_intelligence_agent.schemas import ValidatedData, ValidationError

# Base valid input structure as template
VALID_TEMPLATE = {
    "gstin": "29ABCDE1234F1Z5",
    "pan": "ABCDE1234F",
    "business_registration_date": "2020-01-15",
    "gst_data": {
        "gstin": "29ABCDE1234F1Z5",
        "monthly_revenue": [100000.0] * 12,
        "filing_history": [True] * 12,
        "annual_turnover": 1200000.0
    },
    "upi_transactions": [
        {
            "amount": 5000.50,
            "timestamp": "2024-01-15T10:30:00",
            "counterparty": "Vendor A"
        }
    ],
    "account_aggregator_data": {
        "month_end_balances": [50000.0] * 6,
        "monthly_inflows": [100000.0] * 6,
        "monthly_outflows": [80000.0] * 6,
        "statement_start_date": "2023-01-01",
        "statement_end_date": "2023-06-30"
    }
}


@st.composite
def mutated_input_strategy(draw):
    """Generate inputs by randomly mutating a valid template."""
    import copy
    data = copy.deepcopy(VALID_TEMPLATE)
    
    # Decide which fields to mutate
    mutate_gstin = draw(st.booleans())
    mutate_pan = draw(st.booleans())
    mutate_upi = draw(st.booleans())
    mutate_aa = draw(st.booleans())
    remove_keys = draw(st.lists(st.sampled_from(list(data.keys())), unique=True))
    
    if mutate_gstin:
        data["gstin"] = draw(st.one_of(
            st.just("INVALID_GSTIN"),
            st.just("   "),
            st.just("29ABCDE1234F1Z"),  # short
            st.just("29ABCDE1234F1Z55"),  # long
            st.none(),
            st.integers()
        ))
        
    if mutate_pan:
        data["pan"] = draw(st.one_of(
            st.just("INVALIDPAN"),
            st.just(""),
            st.none(),
            st.integers()
        ))
        
    if mutate_upi:
        # Mutate UPI transactions list or its transactions
        upi_action = draw(st.sampled_from(["empty", "wrong_type", "bad_amount", "missing_fields", "valid"]))
        if upi_action == "empty":
            data["upi_transactions"] = []
        elif upi_action == "wrong_type":
            data["upi_transactions"] = "not a list"
        elif upi_action == "bad_amount":
            data["upi_transactions"] = [{
                "amount": draw(st.one_of(st.floats(max_value=0.0), st.just(100.555), st.none())),
                "timestamp": "2024-01-15T10:30:00",
                "counterparty": "Vendor A"
            }]
        elif upi_action == "missing_fields":
            data["upi_transactions"] = [{
                "amount": 100.0
                # missing timestamp and counterparty
            }]
            
    if mutate_aa:
        # Mutate account aggregator data
        aa_action = draw(st.sampled_from(["missing_start", "missing_end", "short_date_range", "invalid_date_format"]))
        if aa_action == "missing_start":
            data["account_aggregator_data"]["statement_start_date"] = None
        elif aa_action == "missing_end":
            data["account_aggregator_data"]["statement_end_date"] = None
        elif aa_action == "short_date_range":
            data["account_aggregator_data"]["statement_start_date"] = "2023-01-01"
            data["account_aggregator_data"]["statement_end_date"] = "2023-02-01"  # < 90 days
        elif aa_action == "invalid_date_format":
            data["account_aggregator_data"]["statement_start_date"] = "not-a-date"
            
    # Randomly delete some top level keys
    for key in remove_keys:
        if key in data:
            del data[key]
            
    return data


@given(data=mutated_input_strategy())
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_property_validator_robustness(data):
    """**Validates: Requirements 1.1, 1.7**
    
    Property: The validator never raises exceptions, always returns ValidatedData or list of ValidationError.
    If it returns a list of ValidationError, it must be non-empty.
    """
    try:
        result = validate(data)
    except Exception as e:
        pytest.fail(f"Validator raised an unexpected exception: {e}")
        
    if isinstance(result, ValidatedData):
        assert result.status == "VALIDATED"
        assert result.data is not None
    elif isinstance(result, list):
        assert len(result) > 0, "ValidationError list must be non-empty"
        for error in result:
            assert isinstance(error, ValidationError)
            assert error.field is not None
            assert error.error is not None
    else:
        pytest.fail(f"Validator returned an unexpected type: {type(result)}")
