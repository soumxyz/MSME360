import os
import sys
import csv
from agents.agent_one import verify_files, REQUIRED_BANK_COLUMNS, REQUIRED_GST_COLUMNS

# Ensure we can run it from backend/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_agent_one():
    print("========================================================================")
    print("RUNNING AGENT 1 INTEGRATION & VERIFICATION TESTS")
    print("========================================================================")

    dataset_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Dataset")
    bank_csv_path = os.path.join(dataset_dir, "bank_transactions.csv")
    gst_csv_path = os.path.join(dataset_dir, "gst_summary.csv")

    if not os.path.exists(bank_csv_path) or not os.path.exists(gst_csv_path):
        print(f"[FAIL] Dataset files not found at {dataset_dir}. Please run the generator first.")
        sys.exit(1)

    print("[INFO] Loading transaction data for a sample business (MSME001)...")
    
    # 1. Extract data for MSME001
    bank_msme001_rows = []
    with open(bank_csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Business_ID"] == "MSME001":
                bank_msme001_rows.append(row)

    gst_msme001_rows = []
    with open(gst_csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Business_ID"] == "MSME001":
                gst_msme001_rows.append(row)

    print(f"[INFO] Extracted {len(bank_msme001_rows)} bank rows and {len(gst_msme001_rows)} GST rows for MSME001.")

    # Convert back to CSV string to simulate file upload
    def to_csv_string(rows, columns):
        if not rows:
            return ""
        import io
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        for r in rows:
            # only keep standard columns
            writer.writerow({col: r.get(col, "") for col in columns})
        return output.getvalue()

    bank_csv_str = to_csv_string(bank_msme001_rows, REQUIRED_BANK_COLUMNS)
    gst_csv_str = to_csv_string(gst_msme001_rows, REQUIRED_GST_COLUMNS)

    # Test 1: Clean Validation (MSME001 is clean)
    print("\n--- Test 1: Clean MSME001 Upload ---")
    report1 = verify_files(bank_csv_str, gst_csv_str)
    print(f"Readiness: {report1['readiness']}")
    print(f"Errors: {report1['errors']}")
    print(f"Warnings count: {len(report1['warnings'])}")
    print(f"Metrics: {report1['metrics']}")
    
    assert report1['readiness'] in ["GREEN", "YELLOW"], f"Clean MSME001 dataset should not be RED. Got: {report1['readiness']}"
    print("[PASS] Test 1 passed successfully.")

    # Test 2: Missing Columns Schema Check (RED)
    print("\n--- Test 2: Schema Failure (Missing Transaction_ID) ---")
    bad_columns = [col for col in REQUIRED_BANK_COLUMNS if col != "Transaction_ID"]
    bad_bank_csv_str = to_csv_string(bank_msme001_rows, bad_columns)
    report2 = verify_files(bad_bank_csv_str, gst_csv_str)
    print(f"Readiness: {report2['readiness']}")
    print(f"Errors: {report2['errors']}")
    
    assert report2['readiness'] == "RED", "Should yield RED for missing columns."
    assert any("missing required columns" in err for err in report2['errors']), "Should log a missing column error."
    print("[PASS] Test 2 passed successfully.")

    # Test 3: Insufficient Coverage Check (RED)
    print("\n--- Test 3: Coverage Failure (< 6 months of statement) ---")
    # Take first 10 transactions (spans only a few days)
    short_rows = bank_msme001_rows[:10]
    short_bank_csv_str = to_csv_string(short_rows, REQUIRED_BANK_COLUMNS)
    report3 = verify_files(short_bank_csv_str, gst_csv_str)
    print(f"Readiness: {report3['readiness']}")
    print(f"Errors: {report3['errors']}")
    
    assert report3['readiness'] == "RED", "Should yield RED for low date coverage."
    assert any("Insufficient bank statement coverage" in err for err in report3['errors']), "Should log an insufficient coverage error."
    print("[PASS] Test 3 passed successfully.")

    # Test 4: Running Balance Reconciliation Check (YELLOW/RED)
    print("\n--- Test 4: Reconciliation Math Failure ---")
    # Mess up one running balance
    corrupt_rows = [dict(r) for r in bank_msme001_rows]
    if len(corrupt_rows) > 5:
        corrupt_rows[4]["Running_Balance"] = str(float(corrupt_rows[4]["Running_Balance"]) + 5000.0)
    corrupt_bank_csv_str = to_csv_string(corrupt_rows, REQUIRED_BANK_COLUMNS)
    report4 = verify_files(corrupt_bank_csv_str, gst_csv_str)
    print(f"Readiness: {report4['readiness']}")
    print(f"Warnings count: {len(report4['warnings'])}")
    print(f"Warnings snippet: {report4['warnings'][:2]}")
    
    # One reconciliation error will make readiness YELLOW (warnings log)
    assert report4['readiness'] == "YELLOW", "Single reconciliation discrepancy should yield YELLOW."
    assert any("Reconciliation deviation" in warn for warn in report4['warnings']), "Should log a reconciliation warning."
    print("[PASS] Test 4 passed successfully.")

    # Test 5: Severe Mismatch Checks (RED)
    print("\n--- Test 5: Severe Math Discrepancy Failure ---")
    # Mess up all running balances to trigger compromised statement integrity
    heavy_corrupt_rows = [dict(r) for r in bank_msme001_rows]
    for idx, r in enumerate(heavy_corrupt_rows):
        if idx % 2 == 1:
            r["Running_Balance"] = str(float(r["Running_Balance"]) + 10000.0)
    heavy_corrupt_bank_csv_str = to_csv_string(heavy_corrupt_rows, REQUIRED_BANK_COLUMNS)
    report5 = verify_files(heavy_corrupt_bank_csv_str, gst_csv_str)
    print(f"Readiness: {report5['readiness']}")
    print(f"Errors: {report5['errors']}")
    
    assert report5['readiness'] == "RED", "High frequency of balance deviations should yield RED."
    assert any("compromised" in err or "integrity" in err for err in report5['errors']), "Should log compromised statement integrity."
    print("[PASS] Test 5 passed successfully.")

    print("\n========================================================================")
    print("ALL AGENT 1 VALIDATOR TESTS PASSED SUCCESSFULLY!")
    print("========================================================================")


if __name__ == "__main__":
    test_agent_one()
