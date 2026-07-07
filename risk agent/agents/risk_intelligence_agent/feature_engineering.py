"""Feature engineering component for Risk Intelligence Agent.

This module transforms raw validated data into an 8-element feature vector
for ML prediction. Features are computed from GST, UPI, Account Aggregator,
EPFO, and Bank data, then normalized using min-max scaling.

Feature order (MUST be exactly this order):
0: revenue_growth_percentage
1: average_monthly_balance
2: cash_flow_ratio
3: upi_transaction_frequency
4: employee_growth_percentage
5: emi_to_revenue_ratio
6: business_age_months
7: digital_payment_ratio

Null handling: if a feature cannot be computed (insufficient data or division
by zero), set it to -1 in the feature vector.
"""

from datetime import datetime
from typing import Optional, Dict, Tuple
import yaml
from pathlib import Path

from .schemas import ValidatedData, FeatureVector


# Load normalization bounds from config at module initialization
_CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "model_config.yaml"
_NORMALIZATION_BOUNDS: Dict[str, Tuple[float, float]] = {}


def _load_normalization_bounds() -> None:
    """Load normalization bounds from model_config.yaml."""
    global _NORMALIZATION_BOUNDS
    try:
        with open(_CONFIG_PATH, 'r') as f:
            config = yaml.safe_load(f)
            norm_config = config.get('normalization', {})
            
            # Convert list [min, max] to tuple (min, max)
            for feature_name, bounds in norm_config.items():
                if isinstance(bounds, list) and len(bounds) == 2:
                    _NORMALIZATION_BOUNDS[feature_name] = (bounds[0], bounds[1])
    except Exception as e:
        raise RuntimeError(f"Failed to load normalization bounds from config: {e}")


# Initialize normalization bounds at module load
_load_normalization_bounds()


def _normalize(value: Optional[float], feature_name: str) -> float:
    """Normalize a feature value to [0, 1] range using min-max scaling.
    
    Args:
        value: Raw feature value or None
        feature_name: Name of the feature for lookup of min/max bounds
        
    Returns:
        Normalized value in [0, 1], or -1 if value is None
    """
    if value is None:
        return -1.0
    
    if feature_name not in _NORMALIZATION_BOUNDS:
        raise ValueError(f"No normalization bounds found for feature: {feature_name}")
    
    min_val, max_val = _NORMALIZATION_BOUNDS[feature_name]
    
    # If max == min, return 0.5 as per requirement 2.17
    if max_val == min_val:
        return 0.5
    
    normalized = (value - min_val) / (max_val - min_val)
    
    # Clamp to [0, 1] range (in case value is outside training bounds)
    return max(0.0, min(1.0, normalized))


def _compute_revenue_growth_percentage(data: ValidatedData) -> Optional[float]:
    """Compute revenue growth percentage from GST data.
    
    Formula: ((rev_m12 - rev_m1) / rev_m1) * 100
    Null if < 12 months GST data
    
    Returns:
        Growth percentage or None if insufficient data
    """
    monthly_revenue = data.data.gst_data.monthly_revenue
    
    # Need at least 12 months of data
    if len(monthly_revenue) < 12:
        return None
    
    rev_m1 = monthly_revenue[0]  # Oldest month
    rev_m12 = monthly_revenue[11]  # 12th month
    
    # Avoid division by zero
    if rev_m1 == 0:
        return None
    
    growth = ((rev_m12 - rev_m1) / rev_m1) * 100
    return growth


def _compute_average_monthly_balance(data: ValidatedData) -> Optional[float]:
    """Compute average monthly balance from Account Aggregator data.
    
    Formula: mean of month-end balances
    Null if < 6 months AA data
    
    Returns:
        Average balance or None if insufficient data
    """
    month_end_balances = data.data.account_aggregator_data.month_end_balances
    
    # Need at least 6 months of data
    if len(month_end_balances) < 6:
        return None
    
    avg_balance = sum(month_end_balances) / len(month_end_balances)
    return avg_balance


def _compute_cash_flow_ratio(data: ValidatedData) -> Optional[float]:
    """Compute cash flow ratio from Account Aggregator data.
    
    Formula: (inflows - outflows) / inflows
    Null if < 6 months or inflows == 0
    
    Returns:
        Cash flow ratio or None if insufficient data or zero inflows
    """
    aa_data = data.data.account_aggregator_data
    monthly_inflows = aa_data.monthly_inflows
    monthly_outflows = aa_data.monthly_outflows
    
    # Need at least 6 months of data
    if len(monthly_inflows) < 6 or len(monthly_outflows) < 6:
        return None
    
    total_inflows = sum(monthly_inflows)
    total_outflows = sum(monthly_outflows)
    
    # Avoid division by zero
    if total_inflows == 0:
        return None
    
    cash_flow_ratio = (total_inflows - total_outflows) / total_inflows
    return cash_flow_ratio


def _compute_upi_transaction_frequency(data: ValidatedData) -> Optional[float]:
    """Compute UPI transaction frequency.
    
    Formula: total_count / num_months
    Null if < 6 months UPI data
    
    Returns:
        Transaction frequency or None if insufficient data
    """
    upi_transactions = data.data.upi_transactions
    
    if len(upi_transactions) == 0:
        return None
    
    # Calculate time span in months from first to last transaction
    timestamps = [txn.timestamp for txn in upi_transactions]
    timestamps.sort()
    
    first_date = timestamps[0]
    last_date = timestamps[-1]
    
    # Calculate number of months (approximate as days / 30)
    days_span = (last_date - first_date).days
    num_months = max(1, days_span / 30.0)
    
    # Need at least 6 months of data (180 days)
    if days_span < 180:
        return None
    
    total_count = len(upi_transactions)
    frequency = total_count / num_months
    return frequency


def _compute_employee_growth_percentage(data: ValidatedData) -> Optional[float]:
    """Compute employee growth percentage from EPFO data.
    
    Formula: ((emp_m12 - emp_m1) / emp_m1) * 100
    Null if < 12 months EPFO data or emp_m1 == 0
    
    Returns:
        Growth percentage or None if insufficient data
    """
    if data.data.epfo_data is None:
        return None
    
    monthly_employee_counts = data.data.epfo_data.monthly_employee_counts
    
    # Need at least 12 months of data
    if len(monthly_employee_counts) < 12:
        return None
    
    emp_m1 = monthly_employee_counts[0]  # Oldest month
    emp_m12 = monthly_employee_counts[11]  # 12th month
    
    # Avoid division by zero
    if emp_m1 == 0:
        return None
    
    growth = ((emp_m12 - emp_m1) / emp_m1) * 100
    return growth


def _compute_emi_to_revenue_ratio(data: ValidatedData) -> Optional[float]:
    """Compute EMI to revenue ratio from Bank and GST data.
    
    Formula: monthly_emi / avg_monthly_revenue
    Null if revenue == 0
    
    Returns:
        EMI ratio or None if insufficient data or zero revenue
    """
    if data.data.bank_data is None:
        return None
    
    monthly_emi = data.data.bank_data.total_monthly_emi
    monthly_revenue = data.data.gst_data.monthly_revenue
    
    if len(monthly_revenue) == 0:
        return None
    
    avg_monthly_revenue = sum(monthly_revenue) / len(monthly_revenue)
    
    # Avoid division by zero
    if avg_monthly_revenue == 0:
        return None
    
    ratio = monthly_emi / avg_monthly_revenue
    return ratio


def _compute_business_age_months(data: ValidatedData) -> Optional[float]:
    """Compute business age in months.
    
    Formula: months between registration date and current date
    
    Returns:
        Age in months or None if registration date missing
    """
    reg_date = data.data.business_registration_date
    
    if reg_date is None:
        return None
    
    current_date = datetime.now().date()
    
    # Calculate difference in months
    years_diff = current_date.year - reg_date.year
    months_diff = current_date.month - reg_date.month
    
    total_months = years_diff * 12 + months_diff
    
    # Ensure non-negative
    return max(0, total_months)


def _compute_digital_payment_ratio(data: ValidatedData) -> Optional[float]:
    """Compute digital payment ratio.
    
    Formula: total_upi_volume / total_revenue
    Null if revenue == 0
    
    Returns:
        Digital payment ratio or None if zero revenue
    """
    upi_transactions = data.data.upi_transactions
    monthly_revenue = data.data.gst_data.monthly_revenue
    
    # Need at least 6 months of UPI data (approximate check)
    if len(upi_transactions) == 0:
        return None
    
    timestamps = [txn.timestamp for txn in upi_transactions]
    if len(timestamps) > 0:
        timestamps.sort()
        days_span = (timestamps[-1] - timestamps[0]).days
        if days_span < 180:  # Less than 6 months
            return None
    
    total_upi_volume = sum(txn.amount for txn in upi_transactions)
    total_revenue = sum(monthly_revenue)
    
    # Avoid division by zero
    if total_revenue == 0:
        return None
    
    ratio = total_upi_volume / total_revenue
    return ratio


def engineer_features(data: ValidatedData) -> FeatureVector:
    """Transform raw validated data into an 8-element feature vector.
    
    This is the main entry point for feature engineering. It computes all
    8 features, normalizes them, and returns a FeatureVector with exactly
    8 elements in the specified order.
    
    Args:
        data: Validated input data from all sources
        
    Returns:
        FeatureVector with 8 normalized features, null values encoded as -1
        
    Feature order:
        0: revenue_growth_percentage
        1: average_monthly_balance
        2: cash_flow_ratio
        3: upi_transaction_frequency
        4: employee_growth_percentage
        5: emi_to_revenue_ratio
        6: business_age_months
        7: digital_payment_ratio
    """
    # Compute raw features
    raw_features = {
        'revenue_growth_percentage': _compute_revenue_growth_percentage(data),
        'average_monthly_balance': _compute_average_monthly_balance(data),
        'cash_flow_ratio': _compute_cash_flow_ratio(data),
        'upi_transaction_frequency': _compute_upi_transaction_frequency(data),
        'employee_growth_percentage': _compute_employee_growth_percentage(data),
        'emi_to_revenue_ratio': _compute_emi_to_revenue_ratio(data),
        'business_age_months': _compute_business_age_months(data),
        'digital_payment_ratio': _compute_digital_payment_ratio(data),
    }
    
    # Feature names in exact order
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
    
    # Normalize features (returns -1 for None values)
    normalized_values = [
        _normalize(raw_features[name], name)
        for name in feature_names
    ]
    
    # Track which features were null
    null_flags = [raw_features[name] is None for name in feature_names]
    
    return FeatureVector(
        values=normalized_values,
        feature_names=feature_names,
        null_flags=null_flags
    )
