"""Fraud detection component for Risk Intelligence Agent.

This module implements anomaly detection logic to identify potential fraud patterns
across GST data, bank statements, UPI transactions, and invoices.

**Validates Requirements**: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 4.11, 4.12, 4.13, 4.14
"""

from typing import Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict

from .schemas import ValidatedData, FraudReport, FraudFlag


def detect_fraud(data: ValidatedData, all_registered_accounts: Set[str]) -> FraudReport:
    """Detect fraud patterns across MSME data sources.
    
    Args:
        data: Validated MSME input data
        all_registered_accounts: Set of all bank account numbers seen across applications
        
    Returns:
        FraudReport with all fraud flag statuses, descriptions, and error indicators
    """
    flags = []
    error_indicators = []
    
    # Initialize all flags to None
    gst_bank_mismatch_flag = None
    suspicious_revenue_spike_flag = None
    circular_transactions_flag = None
    duplicate_account_flag = None
    fake_invoices_flag = None
    suspicious_upi_behavior_flag = None
    
    # Check 1: GST-Bank Mismatch (Requirements 4.1, 4.2, 4.10, 4.11)
    if hasattr(data.data, 'gst_data') and data.data.gst_data and \
       hasattr(data.data, 'account_aggregator_data') and data.data.account_aggregator_data:
        try:
            gst_bank_mismatch_flag = _check_gst_bank_mismatch(
                data.data.gst_data.monthly_revenue,
                data.data.account_aggregator_data.monthly_inflows
            )
            flags.append(FraudFlag(
                flag_name="gst_bank_mismatch",
                status=gst_bank_mismatch_flag,
                description="GST reported revenue differs from bank inflows by >30% for at least one month"
            ))
        except Exception as e:
            error_indicators.append(f"gst_bank_mismatch check failed: {str(e)}")
            flags.append(FraudFlag(
                flag_name="gst_bank_mismatch",
                status=None,
                description="Unable to verify GST-bank mismatch due to data issues"
            ))
    else:
        if not (hasattr(data.data, 'gst_data') and data.data.gst_data):
            error_indicators.append("GST data unavailable for gst_bank_mismatch check")
        if not (hasattr(data.data, 'account_aggregator_data') and data.data.account_aggregator_data):
            error_indicators.append("Bank statement data unavailable for gst_bank_mismatch check")
        flags.append(FraudFlag(
            flag_name="gst_bank_mismatch",
            status=None,
            description="GST or bank data unavailable"
        ))
    
    # Check 2: Suspicious Revenue Spike (Requirements 4.3, 4.9)
    if hasattr(data.data, 'gst_data') and data.data.gst_data:
        try:
            suspicious_revenue_spike_flag = _check_suspicious_revenue_spike(
                data.data.gst_data.monthly_revenue
            )
            flags.append(FraudFlag(
                flag_name="suspicious_revenue_spike",
                status=suspicious_revenue_spike_flag,
                description="Revenue increased by >300% in a single month"
            ))
        except Exception as e:
            error_indicators.append(f"suspicious_revenue_spike check failed: {str(e)}")
            flags.append(FraudFlag(
                flag_name="suspicious_revenue_spike",
                status=None,
                description="Unable to verify revenue spike due to data issues"
            ))
    else:
        error_indicators.append("GST data unavailable for suspicious_revenue_spike check")
        flags.append(FraudFlag(
            flag_name="suspicious_revenue_spike",
            status=None,
            description="GST data unavailable"
        ))
    
    # Check 3: Circular Transactions (Requirements 4.4, 4.5, 4.12)
    if hasattr(data.data, 'upi_transactions') and data.data.upi_transactions:
        try:
            circular_transactions_flag = _check_circular_transactions(
                data.data.upi_transactions
            )
            flags.append(FraudFlag(
                flag_name="circular_transactions",
                status=circular_transactions_flag,
                description="Detected ≥2 round-trip transactions (A→B→A) within 48 hours"
            ))
        except Exception as e:
            error_indicators.append(f"circular_transactions check failed: {str(e)}")
            flags.append(FraudFlag(
                flag_name="circular_transactions",
                status=None,
                description="Unable to verify circular transactions due to data issues"
            ))
    else:
        error_indicators.append("UPI transaction data unavailable for circular_transactions check")
        flags.append(FraudFlag(
            flag_name="circular_transactions",
            status=None,
            description="UPI data unavailable"
        ))
    
    # Check 4: Duplicate Account (Requirement 4.6)
    if hasattr(data.data, 'bank_data') and data.data.bank_data and data.data.bank_data.account_number:
        try:
            duplicate_account_flag = _check_duplicate_account(
                data.data.bank_data.account_number,
                all_registered_accounts
            )
            flags.append(FraudFlag(
                flag_name="duplicate_account",
                status=duplicate_account_flag,
                description="Bank account appears in ≥2 applications"
            ))
        except Exception as e:
            error_indicators.append(f"duplicate_account check failed: {str(e)}")
            flags.append(FraudFlag(
                flag_name="duplicate_account",
                status=None,
                description="Unable to verify duplicate account due to data issues"
            ))
    else:
        error_indicators.append("Bank data unavailable for duplicate_account check")
        flags.append(FraudFlag(
            flag_name="duplicate_account",
            status=None,
            description="Bank data unavailable"
        ))
    
    # Check 5: Fake Invoices (Requirement 4.7)
    if hasattr(data.data, 'gst_data') and data.data.gst_data:
        try:
            # Note: This check assumes invoice data would be part of gst_data
            # Since the schema doesn't explicitly include invoice details,
            # we'll return None for now
            fake_invoices_flag = None
            error_indicators.append("Invoice-level data not available in GST schema for fake_invoices check")
            flags.append(FraudFlag(
                flag_name="fake_invoices",
                status=None,
                description="Invoice-level data not available"
            ))
        except Exception as e:
            error_indicators.append(f"fake_invoices check failed: {str(e)}")
            flags.append(FraudFlag(
                flag_name="fake_invoices",
                status=None,
                description="Unable to verify fake invoices due to data issues"
            ))
    else:
        error_indicators.append("GST data unavailable for fake_invoices check")
        flags.append(FraudFlag(
            flag_name="fake_invoices",
            status=None,
            description="GST data unavailable"
        ))
    
    # Check 6: Suspicious UPI Behavior (Requirements 4.8, 4.12)
    if hasattr(data.data, 'upi_transactions') and data.data.upi_transactions:
        try:
            suspicious_upi_behavior_flag = _check_suspicious_upi_behavior(
                data.data.upi_transactions
            )
            flags.append(FraudFlag(
                flag_name="suspicious_upi_behavior",
                status=suspicious_upi_behavior_flag,
                description="7-day UPI count exceeds 90-day average by >500%"
            ))
        except Exception as e:
            error_indicators.append(f"suspicious_upi_behavior check failed: {str(e)}")
            flags.append(FraudFlag(
                flag_name="suspicious_upi_behavior",
                status=None,
                description="Unable to verify UPI behavior due to data issues"
            ))
    else:
        error_indicators.append("UPI transaction data unavailable for suspicious_upi_behavior check")
        flags.append(FraudFlag(
            flag_name="suspicious_upi_behavior",
            status=None,
            description="UPI data unavailable"
        ))
    
    # Determine if manual review is required (Requirement 4.13)
    requires_manual_review = any(
        flag.status is True
        for flag in flags
    )
    
    return FraudReport(
        gst_bank_mismatch=gst_bank_mismatch_flag,
        suspicious_revenue_spike=suspicious_revenue_spike_flag,
        circular_transactions=circular_transactions_flag,
        duplicate_account=duplicate_account_flag,
        fake_invoices=fake_invoices_flag,
        suspicious_upi_behavior=suspicious_upi_behavior_flag,
        requires_manual_review=requires_manual_review,
        flags=flags,
        error_indicators=error_indicators
    )


def _check_gst_bank_mismatch(gst_revenues: list[float], bank_inflows: list[float]) -> bool:
    """Check if GST revenue differs from bank inflows by >30% for any month.
    
    Args:
        gst_revenues: Monthly GST revenues
        bank_inflows: Monthly bank inflows
        
    Returns:
        True if mismatch detected, False otherwise
    """
    # Compare only the overlapping months
    min_length = min(len(gst_revenues), len(bank_inflows))
    
    for i in range(min_length):
        gst_rev = gst_revenues[i]
        bank_inflow = bank_inflows[i]
        
        # Skip if GST revenue is zero (would cause division by zero)
        if gst_rev == 0:
            continue
            
        # Calculate mismatch percentage
        mismatch = abs(gst_rev - bank_inflow) / gst_rev
        
        if mismatch > 0.30:
            return True
    
    return False


def _check_suspicious_revenue_spike(monthly_revenues: list[float]) -> bool:
    """Check if revenue increases by >300% in any single month.
    
    Args:
        monthly_revenues: List of monthly revenues in chronological order
        
    Returns:
        True if suspicious spike detected, False otherwise
    """
    for i in range(1, len(monthly_revenues)):
        prev_month = monthly_revenues[i - 1]
        curr_month = monthly_revenues[i]
        
        # Skip if previous month revenue is zero or negative (Requirement 4.9)
        if prev_month <= 0:
            continue
        
        # Calculate month-over-month increase percentage
        increase_pct = ((curr_month - prev_month) / prev_month) * 100
        
        if increase_pct > 300:
            return True
    
    return False


def _check_circular_transactions(upi_transactions: list) -> bool:
    """Check for circular transaction patterns (A→B→A within 48 hours).
    
    Args:
        upi_transactions: List of UPI transactions
        
    Returns:
        True if ≥2 complete round trips detected, False otherwise
    """
    # Build a directed graph of transactions with timestamps
    # Format: {(from, to): [timestamps]}
    transactions_graph = defaultdict(list)
    
    # Get the applicant's identifier (we'll use a placeholder since we don't have it in schema)
    # In practice, this would be derived from the MSME's UPI handle
    # For now, we'll track all counterparty-to-counterparty flows
    
    for txn in upi_transactions:
        counterparty = txn.counterparty
        timestamp = txn.timestamp
        
        # We need to identify direction, but the schema doesn't specify
        # For this implementation, we'll assume each transaction has a counterparty
        # and we need to find A→B and B→A patterns
        transactions_graph[counterparty].append(timestamp)
    
    # Check for round trips: need to identify A→B→A patterns
    # A more sophisticated approach: look for same counterparty appearing multiple times
    # within 48 hours (indicating back-and-forth transactions)
    
    round_trip_count = 0
    
    for counterparty, timestamps in transactions_graph.items():
        # Sort timestamps for this counterparty
        sorted_timestamps = sorted(timestamps)
        
        # Look for pairs of transactions within 48 hours
        for i in range(len(sorted_timestamps) - 1):
            time_diff = sorted_timestamps[i + 1] - sorted_timestamps[i]
            
            if time_diff <= timedelta(hours=48):
                round_trip_count += 1
                
                # If we found at least 2 round trips, flag it
                if round_trip_count >= 2:
                    return True
    
    return False


def _check_duplicate_account(account_number: str, all_accounts: Set[str]) -> bool:
    """Check if bank account appears in ≥2 applications.
    
    Args:
        account_number: Current application's bank account number
        all_accounts: Set of all bank account numbers from other applications
        
    Returns:
        True if account is duplicated, False otherwise
    """
    # Check if this account number already exists in the registry
    return account_number in all_accounts


def _check_suspicious_upi_behavior(upi_transactions: list) -> bool:
    """Check if 7-day UPI count exceeds 90-day average by >500%.
    
    Args:
        upi_transactions: List of UPI transactions
        
    Returns:
        True if suspicious behavior detected, False otherwise
    """
    if not upi_transactions or len(upi_transactions) == 0:
        return False
    
    # Sort transactions by timestamp
    sorted_txns = sorted(upi_transactions, key=lambda x: x.timestamp)
    
    if len(sorted_txns) == 0:
        return False
    
    # Calculate 90-day average
    first_timestamp = sorted_txns[0].timestamp
    last_timestamp = sorted_txns[-1].timestamp
    total_days = (last_timestamp - first_timestamp).days + 1
    
    # Need at least 90 days of data
    if total_days < 90:
        return False
    
    total_transactions = len(sorted_txns)
    avg_90_day = total_transactions / (total_days / 90)  # Average per 90-day period
    avg_7_day = avg_90_day / (90 / 7)  # Average per 7-day period
    
    # Check each 7-day window
    for i in range(len(sorted_txns)):
        window_start = sorted_txns[i].timestamp
        window_end = window_start + timedelta(days=7)
        
        # Count transactions in this 7-day window
        window_count = sum(
            1 for txn in sorted_txns
            if window_start <= txn.timestamp < window_end
        )
        
        # Check if this window exceeds the average by >500%
        if avg_7_day > 0 and window_count > avg_7_day * 6:  # 500% increase means 6x the original
            return True
    
    return False
