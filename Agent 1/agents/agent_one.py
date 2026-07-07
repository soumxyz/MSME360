import csv
import io
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Required columns for schemas
REQUIRED_BANK_COLUMNS = [
    "Transaction_ID", "Business_ID", "Date", "Description", 
    "Transaction_Type", "Payment_Mode", "Category", "Credit", 
    "Debit", "Running_Balance"
]

REQUIRED_GST_COLUMNS = [
    "Business_ID", "Month", "Sales", "Taxable_Sales", "GST_Paid", 
    "GST_Liability", "Return_Filing_Date", "Filed_On_Time", 
    "Late_Days", "Input_Tax_Credit", "Output_Tax", "Refund"
]


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date from ISO format YYYY-MM-DD."""
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d")
    except ValueError:
        return None


def verify_files(
    bank_csv_content: str, 
    gst_csv_content: Optional[str] = None
) -> Dict:
    """
    Agent 1 — Intake & Verification Logic.
    Validates schemas, date coverage, bank statement running balance, 
    and GST-to-bank consistency.
    """
    errors: List[str] = []
    warnings: List[str] = []
    metrics: Dict = {}
    
    # 1. Parse Bank CSV
    bank_rows: List[Dict] = []
    try:
        bank_file = io.StringIO(bank_csv_content.strip())
        reader = csv.DictReader(bank_file)
        if not reader.fieldnames:
            errors.append("Bank statement CSV is empty or has no header.")
            return {
                "readiness": "RED",
                "errors": errors,
                "warnings": warnings,
                "metrics": metrics
            }
        
        # Check required columns
        missing_bank_cols = [col for col in REQUIRED_BANK_COLUMNS if col not in reader.fieldnames]
        if missing_bank_cols:
            errors.append(f"Bank statement CSV is missing required columns: {missing_bank_cols}")
            return {
                "readiness": "RED",
                "errors": errors,
                "warnings": warnings,
                "metrics": metrics
            }
            
        for row in reader:
            bank_rows.append(row)
            
    except Exception as e:
        errors.append(f"Failed to parse Bank statement CSV: {str(e)}")
        return {
            "readiness": "RED",
            "errors": errors,
            "warnings": warnings,
            "metrics": metrics
        }

    if not bank_rows:
        errors.append("Bank statement contains 0 transactions.")
        return {
            "readiness": "RED",
            "errors": errors,
            "warnings": warnings,
            "metrics": metrics
        }

    # Extract primary Business ID
    business_id = bank_rows[0].get("Business_ID", "").strip()
    if not business_id:
        errors.append("First bank transaction row has an empty Business_ID.")
        return {
            "readiness": "RED",
            "errors": errors,
            "warnings": warnings,
            "metrics": metrics
        }
    
    metrics["business_id"] = business_id
    metrics["bank_records_count"] = len(bank_rows)

    # 2. Date Range Coverage Check (Min 6 months / 180 days)
    bank_dates = []
    for r in bank_rows:
        d = parse_date(r["Date"])
        if d is not None:
            bank_dates.append(d)
        else:
            errors.append(f"Invalid date format in bank statement for transaction {r.get('Transaction_ID')}: {r.get('Date')}")

    if len(bank_dates) < len(bank_rows):
        # We had date parsing issues, but let's try to proceed with parsed dates
        pass

    if not bank_dates:
        errors.append("No valid dates found in bank statement.")
        return {
            "readiness": "RED",
            "errors": errors,
            "warnings": warnings,
            "metrics": metrics
        }

    start_date = min(bank_dates)
    end_date = max(bank_dates)
    coverage_days = (end_date - start_date).days
    
    metrics["bank_start_date"] = start_date.strftime("%Y-%m-%d")
    metrics["bank_end_date"] = end_date.strftime("%Y-%m-%d")
    metrics["bank_coverage_days"] = coverage_days

    if coverage_days < 180:
        errors.append(f"Insufficient bank statement coverage. Found {coverage_days} days, required minimum is 180 days (6 months).")

    # 3. Bank Statement Balance Reconciliation Check
    # Sort bank transactions to verify running balance sequence
    try:
        # Sort key: Date, then numeric transaction sequence (from Transaction_ID suffix e.g. MSME001-T000001)
        def get_sort_key(x):
            tx_id = x.get("Transaction_ID", "")
            suffix = 0
            if "T" in tx_id:
                try:
                    suffix = int(tx_id.split("T")[-1])
                except ValueError:
                    pass
            d = parse_date(x["Date"])
            d_val = d if d is not None else datetime.min
            return (d_val, suffix)
            
        bank_rows_sorted = sorted(bank_rows, key=get_sort_key)
    except Exception as e:
        warnings.append(f"Could not reliably sort bank transactions for reconciliation check: {str(e)}")
        bank_rows_sorted = bank_rows

    # Running Balance Verification
    balance_errors = 0
    running_balance = None
    
    for i, row in enumerate(bank_rows_sorted):
        # Verify business ID consistency
        if row.get("Business_ID", "").strip() != business_id:
            errors.append(f"Inconsistent Business_ID in bank transactions. Expected {business_id}, got {row.get('Business_ID')}")
            break

        try:
            credit = float(row["Credit"] or 0)
            debit = float(row["Debit"] or 0)
            recorded_bal = float(row["Running_Balance"] or 0)
        except ValueError:
            errors.append(f"Non-numeric values in financial fields for transaction {row.get('Transaction_ID')}")
            break

        if credit < 0 or debit < 0:
            errors.append(f"Negative values found in Credit/Debit fields for transaction {row.get('Transaction_ID')}")

        if credit > 0 and debit > 0:
            errors.append(f"Both Credit and Debit are non-zero for transaction {row.get('Transaction_ID')}")

        if running_balance is None:
            # First transaction, initialize running balance
            running_balance = recorded_bal
        else:
            expected_bal = running_balance + credit - debit
            if abs(recorded_bal - expected_bal) > 0.05:
                balance_errors += 1
                if balance_errors <= 5:  # Log first 5 errors
                    warnings.append(
                        f"Reconciliation deviation at transaction {row.get('Transaction_ID')}: "
                        f"Expected {expected_bal:.2f}, got {recorded_bal:.2f} (diff: {abs(recorded_bal - expected_bal):.2f})"
                    )
            running_balance = recorded_bal

    if balance_errors > 0:
        if balance_errors > 5:
            warnings.append(f"Total running balance reconciliation mismatch count: {balance_errors} rows.")
        # If mismatch is severe (e.g. cumulative errors or large individual drift), warn or error
        if balance_errors > len(bank_rows) * 0.05: # more than 5% of records have balance drift
            errors.append(f"High frequency of running balance reconciliation failures ({balance_errors} mismatches). Statement integrity compromised.")

    # 4. Parse & Verify GST Summary (if provided)
    gst_rows: List[Dict] = []
    is_gst_consistent = True
    
    if gst_csv_content and gst_csv_content.strip():
        try:
            gst_file = io.StringIO(gst_csv_content.strip())
            reader = csv.DictReader(gst_file)
            
            # Check required columns
            missing_gst_cols = [col for col in REQUIRED_GST_COLUMNS if col not in reader.fieldnames]
            if missing_gst_cols:
                errors.append(f"GST summary CSV is missing required columns: {missing_gst_cols}")
            else:
                for row in reader:
                    gst_rows.append(row)
                    
        except Exception as e:
            errors.append(f"Failed to parse GST summary CSV: {str(e)}")
            
        if gst_rows:
            metrics["gst_records_count"] = len(gst_rows)
            
            # Check Business ID consistency in GST Summary
            for row in gst_rows:
                if row.get("Business_ID", "").strip() != business_id:
                    errors.append(f"GST summary has mismatching Business_ID. Expected {business_id}, got {row.get('Business_ID')}")
                    break
            
            # Month-by-month cross-check (Bank Sales credits vs GST Sales)
            # Aggregate Sales credits from bank statement per month
            bank_sales_by_month: Dict[str, float] = {}
            for row in bank_rows:
                if row.get("Category") == "Sales":
                    date_val = parse_date(row["Date"])
                    if date_val:
                        month_str = date_val.strftime("%Y-%m")
                        credit = float(row.get("Credit") or 0)
                        bank_sales_by_month[month_str] = bank_sales_by_month.get(month_str, 0.0) + credit

            # Verify math consistency in GST filings
            for g in gst_rows:
                month = g.get("Month", "")
                try:
                    gst_sales = float(g.get("Sales") or 0)
                    taxable_sales = float(g.get("Taxable_Sales") or 0)
                    output_tax = float(g.get("Output_Tax") or 0)
                    itc = float(g.get("Input_Tax_Credit") or 0)
                    liability = float(g.get("GST_Liability") or 0)
                    paid = float(g.get("GST_Paid") or 0)
                    late_days = int(g.get("Late_Days") or 0)
                    filed_on_time = g.get("Filed_On_Time", "Yes").strip()
                except ValueError:
                    errors.append(f"Non-numeric fields in GST summary for month {month}")
                    is_gst_consistent = False
                    continue

                # Rule A: Bank Sales vs GST Sales matching
                bank_sales = bank_sales_by_month.get(month, 0.0)
                # Allow minor rounding tolerance of ₹10.0
                if abs(bank_sales - gst_sales) > 10.0:
                    is_gst_consistent = False
                    warnings.append(
                        f"Revenue discrepancy in {month}: Bank Sales (Credits in 'Sales' category) = ₹{bank_sales:.2f}, "
                        f"GST Sales reported = ₹{gst_sales:.2f} (diff: ₹{abs(bank_sales - gst_sales):.2f})"
                    )

                # Rule B: Sales - Taxable_Sales == Output_Tax
                if abs((gst_sales - taxable_sales) - output_tax) > 10.0:
                    is_gst_consistent = False
                    warnings.append(
                        f"GST calculation mismatch in {month}: Sales - Taxable_Sales = ₹{(gst_sales - taxable_sales):.2f}, "
                        f"but Output_Tax = ₹{output_tax:.2f}"
                    )

                # Rule C: Liability == max(0, Output_Tax - Input_Tax_Credit)
                expected_liab = max(0.0, output_tax - itc)
                if abs(liability - expected_liab) > 10.0:
                    is_gst_consistent = False
                    warnings.append(
                        f"GST liability mismatch in {month}: Expected ₹{expected_liab:.2f}, reported liability = ₹{liability:.2f}"
                    )

                # Rule D: Liability == GST_Paid (taxes due must be settled)
                if abs(liability - paid) > 10.0:
                    is_gst_consistent = False
                    warnings.append(
                        f"GST payment mismatch in {month}: Liability = ₹{liability:.2f}, but GST Paid = ₹{paid:.2f}"
                    )

                # Rule E: Filed_On_Time and Late_Days agreement
                if filed_on_time == "No" and late_days <= 0:
                    warnings.append(f"GST return filed late on {month} but Late_Days is {late_days}")
                elif filed_on_time == "Yes" and late_days > 0:
                    warnings.append(f"GST return marked filed on time for {month} but Late_Days is {late_days}")

            metrics["is_gst_consistent"] = is_gst_consistent
    else:
        # GST summary not provided. Check if registered in businesses.csv? 
        # Since businesses.csv is not uploaded to Agent 1 directly (Agent 1 only gets bank statement + GST summary),
        # we issue a warning that GST summary was not provided.
        warnings.append("No GST summary CSV was uploaded. Scoring engine will default to bank-only feature calculations.")
        metrics["gst_records_count"] = 0
        metrics["is_gst_consistent"] = None

    # 5. Determine Readiness status
    if errors:
        readiness = "RED"
    elif warnings:
        # Check if warnings are severe enough to downgrade to RED or keep at YELLOW
        # Large revenue discrepancy in GST (e.g. > 10% mismatch) triggers RED
        heavy_gst_discrepancy = False
        for w in warnings:
            if "Revenue discrepancy" in w:
                # Parse out numbers or flag as yellow. Let's keep it as YELLOW for now, unless errors exist
                pass
        readiness = "YELLOW"
    else:
        readiness = "GREEN"

    return {
        "readiness": readiness,
        "errors": errors,
        "warnings": warnings,
        "metrics": metrics
    }
