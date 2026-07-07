"""Property-based tests for Fraud Engine using Hypothesis.

Validates Property 4: Fraud-Manual-Review Implication
Requirements: 4.13
"""

import pytest
import sys
from pathlib import Path
from hypothesis import given, strategies as st, settings, HealthCheck

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.risk_intelligence_agent.fraud_engine import detect_fraud
from agents.risk_intelligence_agent.schemas import (
    ValidatedData,
    MSMEInput,
    GSTData,
    UPITransaction,
    AccountAggregatorData,
    EPFOData,
    BankData
)
from datetime import date, datetime, timedelta


@st.composite
def validated_data_for_fraud_strategy(draw):
    """Generate ValidatedData with random inputs for fraud checks."""
    
    # Decide if there is a fraud flag triggered or not
    gst_bank_mismatch = draw(st.booleans())
    suspicious_revenue_spike = draw(st.booleans())
    circular_transactions = draw(st.booleans())
    duplicate_account = draw(st.booleans())
    suspicious_upi = draw(st.booleans())
    
    # Standard values
    gstin = "29ABCDE1234F1Z5"
    pan = "ABCDE1234F"
    business_reg_date = date(2020, 1, 1)
    
    # GST monthly revenue
    if suspicious_revenue_spike:
        # MoM increase > 300% (e.g. from 10k to 50k, which is 400% increase)
        monthly_revenue = [10000.0] * 5 + [50000.0] + [10000.0] * 6
    else:
        # Standard stable revenue
        monthly_revenue = [10000.0] * 12
        
    annual_turnover = sum(monthly_revenue)
    gst_data = GSTData(
        gstin=gstin,
        monthly_revenue=monthly_revenue,
        filing_history=[True] * 12,
        annual_turnover=annual_turnover
    )
    
    # Account Aggregator inflows/outflows
    if gst_bank_mismatch:
        # GST monthly rev and bank inflow differ by >30% (e.g. GST rev=10k, Bank inflow=20k)
        monthly_inflows = [20000.0] * 6
    else:
        # Matches GST revenue (10k)
        monthly_inflows = [10000.0] * 6
        
    aa_data = AccountAggregatorData(
        month_end_balances=[50000.0] * 6,
        monthly_inflows=monthly_inflows,
        monthly_outflows=[5000.0] * 6,
        statement_start_date=date(2023, 1, 1),
        statement_end_date=date(2023, 6, 30)
    )
    
    # UPI Transactions
    upi_transactions = []
    if circular_transactions:
        # A->B->A round trip within 48h (we simulate this by adding duplicate counterparties within 48h)
        base_time = datetime(2024, 1, 1, 12, 0, 0)
        # 2 round trips to counterparty1
        upi_transactions.extend([
            UPITransaction(amount=100.0, timestamp=base_time, counterparty="CP_1"),
            UPITransaction(amount=100.0, timestamp=base_time + timedelta(hours=10), counterparty="CP_1"),
            UPITransaction(amount=200.0, timestamp=base_time + timedelta(days=5), counterparty="CP_1"),
            UPITransaction(amount=200.0, timestamp=base_time + timedelta(days=5, hours=10), counterparty="CP_1"),
        ])
    elif suspicious_upi:
        # 7-day count exceeds 90-day average by >500%
        # Needs 90 days total. Let's make 90 days with 1 transaction every 10 days (9 total).
        # And in a single 7-day window, we add 50 transactions.
        base_time = datetime(2024, 1, 1)
        for d in range(0, 90, 10):
            upi_transactions.append(UPITransaction(amount=10.0, timestamp=base_time + timedelta(days=d), counterparty="CP_A"))
        # Add 50 transactions in the last week
        for _ in range(50):
            upi_transactions.append(UPITransaction(amount=10.0, timestamp=base_time + timedelta(days=85), counterparty="CP_B"))
    else:
        # Normal UPI transactions
        upi_transactions = [
            UPITransaction(amount=100.0, timestamp=datetime(2024, 1, 1) + timedelta(days=i), counterparty=f"CP_{i}")
            for i in range(10)
        ]
        
    # Bank Data (for duplicate account test)
    account_number = "1234567890" if not duplicate_account else "DUP_ACC_123"
    bank_data = BankData(
        total_monthly_emi=2000.0,
        loan_amounts=[50000.0],
        account_number=account_number
    )
    
    msme_input = MSMEInput(
        gstin=gstin,
        pan=pan,
        business_registration_date=business_reg_date,
        gst_data=gst_data,
        upi_transactions=upi_transactions,
        account_aggregator_data=aa_data,
        bank_data=bank_data
    )
    
    data_sources = ["GST", "UPI", "AA", "BANK"]
    
    return ValidatedData(
        status="VALIDATED",
        data=msme_input,
        data_sources_available=data_sources
    ), duplicate_account


@given(inp_data=validated_data_for_fraud_strategy())
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_property_fraud_manual_review_implication(inp_data):
    """**Validates: Requirements 4.13**
    
    Property: If any fraud flag is TRUE, then requires_manual_review must be TRUE.
    Also, requires_manual_review must be a boolean.
    """
    raw_data, duplicate_account = inp_data
    
    # We pass in the registered accounts set. If duplicate_account is True,
    # the set contains the account number, triggering the check.
    registered_accounts = set()
    if duplicate_account:
        registered_accounts.add("DUP_ACC_123")
        
    result = detect_fraud(raw_data, registered_accounts)
    
    assert isinstance(result.requires_manual_review, bool)
    
    # Check if any flag status is True
    any_flag_true = any(flag.status is True for flag in result.flags)
    
    if any_flag_true:
        assert result.requires_manual_review is True, \
            f"Expected requires_manual_review=True since a fraud flag was True. Flags: {result.flags}"
    else:
        # If no flags are True, requires_manual_review should be False
        assert result.requires_manual_review is False, \
            f"Expected requires_manual_review=False since no fraud flag was True. Flags: {result.flags}"
