"""Unit tests for validator component."""

from datetime import date, datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.risk_intelligence_agent.validator import validate
from agents.risk_intelligence_agent.schemas import ValidatedData, ValidationError


def create_valid_input() -> dict:
    """Create a valid MSME input for testing."""
    today = date.today()
    statement_end = today
    statement_start = today - timedelta(days=100)  # >90 days
    
    return {
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
            },
            {
                "amount": 3200.00,
                "timestamp": "2024-01-16T14:20:00",
                "counterparty": "Vendor B"
            }
        ],
        "account_aggregator_data": {
            "month_end_balances": [50000.0] * 6,
            "monthly_inflows": [100000.0] * 6,
            "monthly_outflows": [80000.0] * 6,
            "statement_start_date": statement_start.isoformat(),
            "statement_end_date": statement_end.isoformat()
        }
    }


def test_valid_input():
    """Test validation with completely valid input."""
    data = create_valid_input()
    result = validate(data)
    
    assert isinstance(result, ValidatedData), f"Expected ValidatedData, got {type(result)}"
    assert result.status == "VALIDATED"
    assert "GST" in result.data_sources_available
    assert "UPI" in result.data_sources_available
    assert "Account_Aggregator" in result.data_sources_available


def test_invalid_gstin_format():
    """Test validation fails for invalid GSTIN format."""
    data = create_valid_input()
    data["gstin"] = "INVALID_GSTIN"
    data["gst_data"]["gstin"] = "INVALID_GSTIN"
    
    result = validate(data)
    
    assert isinstance(result, list), "Expected list of ValidationError"
    assert len(result) > 0
    assert any("GSTIN format invalid" in error.error for error in result)


def test_invalid_pan_format():
    """Test validation fails for invalid PAN format."""
    data = create_valid_input()
    data["pan"] = "INVALID123"
    
    result = validate(data)
    
    assert isinstance(result, list), "Expected list of ValidationError"
    assert len(result) > 0
    assert any("PAN format invalid" in error.error for error in result)


def test_upi_amount_negative():
    """Test validation fails for negative UPI amount."""
    data = create_valid_input()
    data["upi_transactions"][0]["amount"] = -100.50
    
    result = validate(data)
    
    assert isinstance(result, list), "Expected list of ValidationError"
    assert len(result) > 0
    assert any("must be positive" in error.error for error in result)


def test_upi_amount_too_many_decimals():
    """Test validation fails for UPI amount with >2 decimal places."""
    data = create_valid_input()
    data["upi_transactions"][0]["amount"] = 100.555
    
    result = validate(data)
    
    assert isinstance(result, list), "Expected list of ValidationError"
    assert len(result) > 0
    assert any("maximum 2 decimal places" in error.error for error in result)


def test_bank_statement_insufficient_days():
    """Test validation fails for bank statement < 90 days."""
    data = create_valid_input()
    today = date.today()
    data["account_aggregator_data"]["statement_end_date"] = today.isoformat()
    data["account_aggregator_data"]["statement_start_date"] = (today - timedelta(days=60)).isoformat()
    
    result = validate(data)
    
    assert isinstance(result, list), "Expected list of ValidationError"
    assert len(result) > 0
    assert any("at least 90 consecutive days" in error.error for error in result)


def test_missing_required_field():
    """Test validation fails when required field is missing."""
    data = create_valid_input()
    del data["gstin"]
    
    result = validate(data)
    
    assert isinstance(result, list), "Expected list of ValidationError"
    assert len(result) > 0
    assert any("gstin" in error.field.lower() for error in result)


def test_upi_transaction_missing_fields():
    """Test validation fails when UPI transaction missing required fields."""
    data = create_valid_input()
    data["upi_transactions"][0] = {"amount": 100.0}  # Missing timestamp and counterparty
    
    result = validate(data)
    
    assert isinstance(result, list), "Expected list of ValidationError"
    assert len(result) > 0
    # Should have errors for missing timestamp and counterparty
    error_fields = [error.field for error in result]
    assert any("timestamp" in field for field in error_fields)
    assert any("counterparty" in field for field in error_fields)


def test_exhaustive_error_collection():
    """Test that validator collects ALL errors before returning."""
    data = create_valid_input()
    # Introduce multiple errors
    data["gstin"] = "INVALID"
    data["pan"] = "BAD"
    data["upi_transactions"][0]["amount"] = -50.0
    
    result = validate(data)
    
    assert isinstance(result, list), "Expected list of ValidationError"
    # Should have at least 3 errors (invalid GSTIN, invalid PAN, negative amount)
    assert len(result) >= 3, f"Expected at least 3 errors, got {len(result)}"


def test_whitespace_only_fields():
    """Test validation fails for fields containing only whitespace."""
    data = create_valid_input()
    data["gstin"] = "   "
    
    result = validate(data)
    
    assert isinstance(result, list), "Expected list of ValidationError"
    assert len(result) > 0
    assert any("whitespace" in error.error.lower() for error in result)


if __name__ == "__main__":
    print("Running validator tests...")
    
    tests = [
        test_valid_input,
        test_invalid_gstin_format,
        test_invalid_pan_format,
        test_upi_amount_negative,
        test_upi_amount_too_many_decimals,
        test_bank_statement_insufficient_days,
        test_missing_required_field,
        test_upi_transaction_missing_fields,
        test_exhaustive_error_collection,
        test_whitespace_only_fields
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: Unexpected error: {str(e)}")
            failed += 1
    
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
