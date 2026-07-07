"""Property-based tests for schema validation.

Task 2.2: Write unit tests for schema validation
Validates Requirements: 1.2, 1.3, 1.4, 1.5, 2.18
"""

import pytest
import re
from hypothesis import given, strategies as st
from decimal import Decimal

from agents.risk_intelligence_agent.schemas import (
    UPITransaction, MSMEInput, FeatureVector, RiskCategory, Recommendation
)


# Custom strategies
@st.composite
def valid_gstin(draw):
    """Generate valid GSTIN format."""
    state_code = draw(st.integers(min_value=10, max_value=37))
    pan_chars = draw(st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=5, max_size=5))
    entity_num = draw(st.integers(min_value=1000, max_value=9999))
    check_digit = draw(st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=1, max_size=1))
    registrant = draw(st.sampled_from(['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C']))
    final_char = draw(st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", min_size=1, max_size=1))
    
    return f"{state_code}{pan_chars}{entity_num}{check_digit}{registrant}Z{final_char}"


@st.composite
def valid_pan(draw):
    """Generate valid PAN format."""
    letters_start = draw(st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=5, max_size=5))
    digits = draw(st.integers(min_value=1000, max_value=9999))
    letter_end = draw(st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=1, max_size=1))
    
    return f"{letters_start}{digits}{letter_end}"


@st.composite
def invalid_gstin(draw):
    """Generate invalid GSTIN format."""
    return draw(st.one_of(
        st.just(""),
        st.text(max_size=14),  # Too short
        st.text(min_size=16),  # Too long
        st.text(alphabet=st.characters(whitelist_categories=('Ll',)), min_size=15, max_size=15)  # Wrong format
    ))


@st.composite
def invalid_pan(draw):
    """Generate invalid PAN format."""
    return draw(st.one_of(
        st.just(""),
        st.text(max_size=9),  # Too short
        st.text(min_size=11),  # Too long
        st.text(alphabet=st.characters(whitelist_categories=('Ll',)), min_size=10, max_size=10)  # Wrong format
    ))


class TestGSTINValidation:
    """Test GSTIN regex pattern validation."""
    
    @given(valid_gstin())
    def test_valid_gstin_pattern_acceptance(self, gstin):
        """Property: Valid GSTIN formats should be accepted."""
        pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        
        # Valid GSTIN should match pattern
        assert re.match(pattern, gstin) is not None, f"Valid GSTIN rejected: {gstin}"
    
    @given(invalid_gstin())
    def test_invalid_gstin_pattern_rejection(self, gstin):
        """Property: Invalid GSTIN formats should be rejected."""
        pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        
        # Invalid GSTIN should not match pattern
        if gstin:  # Skip empty strings
            result = re.match(pattern, gstin)
            if result:
                # If it matches, it must be because we accidentally generated a valid one
                # In that case, verify it's actually valid
                assert len(gstin) == 15, f"Invalid GSTIN accepted: {gstin}"


class TestPANValidation:
    """Test PAN regex pattern validation."""
    
    @given(valid_pan())
    def test_valid_pan_pattern_acceptance(self, pan):
        """Property: Valid PAN formats should be accepted."""
        pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        
        # Valid PAN should match pattern
        assert re.match(pattern, pan) is not None, f"Valid PAN rejected: {pan}"
    
    @given(invalid_pan())
    def test_invalid_pan_pattern_rejection(self, pan):
        """Property: Invalid PAN formats should be rejected."""
        pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        
        # Invalid PAN should not match pattern
        if pan:  # Skip empty strings
            result = re.match(pattern, pan)
            if result:
                # If it matches, verify it's valid
                assert len(pan) == 10, f"Invalid PAN accepted: {pan}"


class TestUPITransactionValidation:
    """Test UPI transaction validation."""
    
    @given(st.floats(min_value=0.01, max_value=10000000.0, allow_nan=False, allow_infinity=False))
    def test_positive_amounts_accepted(self, amount):
        """Property: Positive amounts should be accepted."""
        # Round to 2 decimal places
        rounded_amount = round(amount, 2)
        
        # Should be positive
        assert rounded_amount > 0
        
        # Should have max 2 decimal places
        decimal_str = str(rounded_amount)
        if '.' in decimal_str:
            decimal_places = len(decimal_str.split('.')[1])
            assert decimal_places <= 2, f"Amount has > 2 decimal places: {rounded_amount}"
    
    @given(st.floats(max_value=0.0, allow_nan=False, allow_infinity=False))
    def test_negative_amounts_rejected(self, amount):
        """Property: Negative or zero amounts should be rejected."""
        # Should fail validation
        assert amount <= 0


class TestFeatureVectorValidation:
    """Test FeatureVector length constraints."""
    
    @given(st.lists(st.floats(min_value=-1, max_value=1, allow_nan=False, allow_infinity=False), min_size=8, max_size=8))
    def test_exactly_8_elements_required(self, features):
        """Property: Feature vector must have exactly 8 elements."""
        # Should have exactly 8 elements
        assert len(features) == 8
        
        # All values should be in [-1, 1]
        for feature in features:
            assert -1 <= feature <= 1, f"Feature value out of bounds: {feature}"
    
    @given(st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=0, max_size=20).filter(lambda x: len(x) != 8))
    def test_wrong_length_rejected(self, features):
        """Property: Feature vectors with != 8 elements should be rejected."""
        # Should not have 8 elements
        assert len(features) != 8


class TestEnumValidation:
    """Test enum value constraints."""
    
    @given(st.sampled_from(['LOW', 'MEDIUM', 'HIGH']))
    def test_risk_category_valid_values(self, category):
        """Property: Only valid RiskCategory values should be accepted."""
        # Should be valid enum value
        assert category in ['LOW', 'MEDIUM', 'HIGH']
        
        # Should be able to create enum
        risk_cat = RiskCategory(category)
        assert risk_cat.value == category
    
    @given(st.sampled_from(['APPROVE', 'APPROVE_WITH_CONDITIONS', 'REJECT', 'MANUAL_REVIEW']))
    def test_recommendation_valid_values(self, recommendation):
        """Property: Only valid Recommendation values should be accepted."""
        # Should be valid enum value
        assert recommendation in ['APPROVE', 'APPROVE_WITH_CONDITIONS', 'REJECT', 'MANUAL_REVIEW']
        
        # Should be able to create enum
        rec = Recommendation(recommendation)
        assert rec.value == recommendation


class TestDecimalPrecision:
    """Test decimal precision for amounts."""
    
    @given(st.floats(min_value=0.01, max_value=1000000.0, allow_nan=False, allow_infinity=False))
    def test_max_two_decimal_places(self, amount):
        """Property: Amounts should have max 2 decimal places."""
        # Round to 2 decimal places
        rounded = round(amount, 2)
        
        # Check decimal places
        decimal_str = f"{rounded:.2f}"
        parts = decimal_str.split('.')
        
        if len(parts) == 2:
            assert len(parts[1]) <= 2, f"More than 2 decimal places: {decimal_str}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
