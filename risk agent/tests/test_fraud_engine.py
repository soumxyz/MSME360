"""Unit tests for Fraud Detection Engine.

Validates: Requirements 4.1, 4.2, 4.3, 4.9, 4.10, 4.11, 4.12
"""

import pytest
from datetime import date, datetime, timedelta
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


def create_validated_data_base() -> MSMEInput:
    """Helper to create a valid baseline MSMEInput."""
    gstin = "29ABCDE1234F1Z5"
    pan = "ABCDE1234F"
    business_reg_date = date(2020, 1, 1)
    
    gst_data = GSTData(
        gstin=gstin,
        monthly_revenue=[100000.0] * 12,
        filing_history=[True] * 12,
        annual_turnover=1200000.0
    )
    
    aa_data = AccountAggregatorData(
        month_end_balances=[50000.0] * 6,
        monthly_inflows=[100000.0] * 6,
        monthly_outflows=[80000.0] * 6,
        statement_start_date=date(2023, 1, 1),
        statement_end_date=date(2023, 6, 30)
    )
    
    return MSMEInput(
        gstin=gstin,
        pan=pan,
        business_registration_date=business_reg_date,
        gst_data=gst_data,
        upi_transactions=[],
        account_aggregator_data=aa_data
    )


def test_gst_bank_mismatch_exact_threshold():
    """Test GST-bank mismatch threshold comparison (exact 30%)."""
    # Mismatch of exactly 30% should not trigger (needs to be > 30%)
    # GST = 100k, Bank Inflow = 130k -> 30% mismatch exactly
    inp = create_validated_data_base()
    inp.gst_data.monthly_revenue = [100000.0] * 12
    inp.account_aggregator_data.monthly_inflows = [130000.0] * 6
    
    v_data = ValidatedData(status="VALIDATED", data=inp, data_sources_available=["GST", "UPI", "AA"])
    res = detect_fraud(v_data, set())
    assert res.gst_bank_mismatch is False

    # Mismatch of 30.1% should trigger
    inp = create_validated_data_base()
    inp.gst_data.monthly_revenue = [100000.0] * 12
    inp.account_aggregator_data.monthly_inflows = [130100.0] * 6
    
    v_data = ValidatedData(status="VALIDATED", data=inp, data_sources_available=["GST", "UPI", "AA"])
    res = detect_fraud(v_data, set())
    assert res.gst_bank_mismatch is True


def test_revenue_spike_zero_or_negative_prev_month():
    """Test revenue spike check handles zero or negative previous month correctly."""
    # Prev month zero -> should be skipped, not trigger spike
    inp = create_validated_data_base()
    inp.gst_data.monthly_revenue = [0.0, 50000.0] + [10000.0] * 10
    
    v_data = ValidatedData(status="VALIDATED", data=inp, data_sources_available=["GST", "UPI", "AA"])
    res = detect_fraud(v_data, set())
    assert res.suspicious_revenue_spike is False

    # Normal spike >300% (from 10k to 50k is 400% spike)
    inp = create_validated_data_base()
    inp.gst_data.monthly_revenue = [10000.0, 50000.0] + [10000.0] * 10
    
    v_data = ValidatedData(status="VALIDATED", data=inp, data_sources_available=["GST", "UPI", "AA"])
    res = detect_fraud(v_data, set())
    assert res.suspicious_revenue_spike is True


def test_circular_transactions_complex_graph():
    """Test circular transaction detection with complex timestamp spacing."""
    # 2 round trips:
    # 1. CP_A at T0, CP_A at T0 + 10 hours (within 48 hours) -> 1 round trip
    # 2. CP_A at T0 + 5 days, CP_A at T0 + 5 days + 10 hours (within 48 hours) -> 2nd round trip
    # This should trigger circular transaction detection.
    inp = create_validated_data_base()
    base_time = datetime(2024, 1, 1, 12, 0, 0)
    inp.upi_transactions = [
        UPITransaction(amount=100.0, timestamp=base_time, counterparty="CP_A"),
        UPITransaction(amount=100.0, timestamp=base_time + timedelta(hours=10), counterparty="CP_A"),
        UPITransaction(amount=200.0, timestamp=base_time + timedelta(days=5), counterparty="CP_A"),
        UPITransaction(amount=200.0, timestamp=base_time + timedelta(days=5, hours=10), counterparty="CP_A")
    ]
    
    v_data = ValidatedData(status="VALIDATED", data=inp, data_sources_available=["GST", "UPI", "AA"])
    res = detect_fraud(v_data, set())
    assert res.circular_transactions is True

    # 1 round trip only (not enough)
    inp = create_validated_data_base()
    inp.upi_transactions = [
        UPITransaction(amount=100.0, timestamp=base_time, counterparty="CP_A"),
        UPITransaction(amount=100.0, timestamp=base_time + timedelta(hours=10), counterparty="CP_A")
    ]
    
    v_data = ValidatedData(status="VALIDATED", data=inp, data_sources_available=["GST", "UPI", "AA"])
    res = detect_fraud(v_data, set())
    assert res.circular_transactions is False


def test_missing_data_sources():
    """Test missing data sources result in None flags and populated error indicators."""
    # Omit UPI and Bank data
    inp = create_validated_data_base()
    inp.upi_transactions = []
    inp.bank_data = None
    
    # We pass ValidatedData with only GST and AA
    v_data = ValidatedData(status="VALIDATED", data=inp, data_sources_available=["GST", "AA"])
    
    res = detect_fraud(v_data, set())
    
    # duplicate_account and circular_transactions should be None/False depending on logic,
    # let's verify duplicate_account is None (since no bank_data is present).
    assert res.duplicate_account is None
    assert any("Bank data unavailable" in err for err in res.error_indicators)
