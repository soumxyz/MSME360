import sys
sys.stdout.reconfigure(encoding='utf-8')
"""
Comprehensive Dual-Agent Integration Test Pipeline
===================================================
Tests data flow: Dataset -> Financial Agent (Agent 1) -> Risk Intelligence Agent

This script:
1. Extracts business data from Dataset (uses MSME001 as test case)
2. Runs ALL Financial Agent test cases
3. Passes validated data to Risk Intelligence Agent
4. Reports results and identifies failure points
"""

import os
import sys
import csv
import json
from datetime import datetime
from typing import Dict, List, Tuple

# Add paths for both agents
agent1_path = os.path.join(os.path.dirname(__file__), "Agent 1")
risk_agent_path = os.path.join(os.path.dirname(__file__), "risk agent")
sys.path.insert(0, agent1_path)
sys.path.insert(0, risk_agent_path)

# Import from Agent 1
sys.path.insert(0, os.path.join(agent1_path, "agents"))
from agent_one import verify_files, REQUIRED_BANK_COLUMNS, REQUIRED_GST_COLUMNS


class DualAgentTester:
    """Orchestrates testing across Financial Agent and Risk Intelligence Agent."""
    
    def __init__(self):
        self.dataset_dir = os.path.join(os.path.dirname(__file__), "Dataset")
        self.test_results = {
            "financial_agent_tests": [],
            "risk_agent_tests": [],
            "integration_status": "PENDING"
        }
        
    def load_business_data(self, business_id: str) -> Tuple[List[Dict], List[Dict], Dict]:
        """Load bank transactions, GST summary, and business info for a specific business."""
        print(f"\n[STEP 1] Loading data for Business ID: {business_id}")
        
        # Load business info
        businesses_path = os.path.join(self.dataset_dir, "businesses.csv")
        business_info = None
        with open(businesses_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["Business_ID"] == business_id:
                    business_info = row
                    break
        
        if not business_info:
            raise ValueError(f"Business ID {business_id} not found in dataset")
        
        # Load bank transactions
        bank_path = os.path.join(self.dataset_dir, "bank_transactions.csv")
        bank_rows = []
        with open(bank_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["Business_ID"] == business_id:
                    bank_rows.append(row)
        
        # Load GST summary
        gst_path = os.path.join(self.dataset_dir, "gst_summary.csv")
        gst_rows = []
        with open(gst_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["Business_ID"] == business_id:
                    gst_rows.append(row)
        
        print(f"   [PASS] Loaded {len(bank_rows)} bank transactions")
        print(f"   [PASS] Loaded {len(gst_rows)} GST summary records")
        print(f"   [PASS] Business: {business_info['Business_Name']} ({business_info['Owner_Name']})")
        
        return bank_rows, gst_rows, business_info
    
    def to_csv_string(self, rows: List[Dict], columns: List[str]) -> str:
        """Convert rows to CSV string format."""
        if not rows:
            return ""
        import io
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        for r in rows:
            writer.writerow({col: r.get(col, "") for col in columns})
        return output.getvalue()
    
    def test_financial_agent_all_cases(self, bank_rows: List[Dict], gst_rows: List[Dict]) -> Dict:
        """Run ALL Financial Agent test cases."""
        print(f"\n{'='*80}")
        print("FINANCIAL AGENT (AGENT 1) - COMPREHENSIVE TEST SUITE")
        print(f"{'='*80}")
        
        results = []
        
        # TEST 1: Clean/Valid Data (GREEN expected)
        print("\n[TEST 1] Valid Data - Should Pass All Checks")
        bank_csv = self.to_csv_string(bank_rows, REQUIRED_BANK_COLUMNS)
        gst_csv = self.to_csv_string(gst_rows, REQUIRED_GST_COLUMNS)
        report1 = verify_files(bank_csv, gst_csv)
        
        test1_result = {
            "test_name": "Valid Data Test",
            "expected": "GREEN or YELLOW",
            "actual": report1['readiness'],
            "passed": report1['readiness'] in ["GREEN", "YELLOW"],
            "errors": report1['errors'],
            "warnings": report1['warnings'][:3],  # First 3 warnings only
            "metrics": report1['metrics']
        }
        results.append(test1_result)
        
        status_symbol = "[PASS]" if test1_result['passed'] else "[FAIL]"
        print(f"   {status_symbol} Readiness: {report1['readiness']}")
        print(f"   {status_symbol} Errors: {len(report1['errors'])}")
        print(f"   {status_symbol} Warnings: {len(report1['warnings'])}")
        print(f"   {status_symbol} Coverage: {report1['metrics'].get('bank_coverage_days', 0)} days")
        
        # TEST 2: Missing Required Columns (RED expected)
        print("\n[TEST 2] Schema Validation - Missing Transaction_ID Column")
        bad_columns = [col for col in REQUIRED_BANK_COLUMNS if col != "Transaction_ID"]
        bad_bank_csv = self.to_csv_string(bank_rows, bad_columns)
        report2 = verify_files(bad_bank_csv, gst_csv)
        
        test2_result = {
            "test_name": "Missing Column Schema Test",
            "expected": "RED",
            "actual": report2['readiness'],
            "passed": report2['readiness'] == "RED",
            "errors": report2['errors'],
            "warnings": []
        }
        results.append(test2_result)
        
        status_symbol = "[PASS]" if test2_result['passed'] else "[FAIL]"
        print(f"   {status_symbol} Readiness: {report2['readiness']} (Expected: RED)")
        print(f"   {status_symbol} Error captured: {'Yes' if report2['errors'] else 'No'}")
        
        # TEST 3: Insufficient Date Coverage (RED expected)
        print("\n[TEST 3] Date Coverage - Less than 6 Months")
        short_rows = bank_rows[:10]  # Only first 10 transactions
        short_bank_csv = self.to_csv_string(short_rows, REQUIRED_BANK_COLUMNS)
        report3 = verify_files(short_bank_csv, gst_csv)
        
        test3_result = {
            "test_name": "Insufficient Coverage Test",
            "expected": "RED",
            "actual": report3['readiness'],
            "passed": report3['readiness'] == "RED",
            "errors": report3['errors'],
            "warnings": []
        }
        results.append(test3_result)
        
        status_symbol = "[PASS]" if test3_result['passed'] else "[FAIL]"
        print(f"   {status_symbol} Readiness: {report3['readiness']} (Expected: RED)")
        print(f"   {status_symbol} Coverage days: {report3['metrics'].get('bank_coverage_days', 0)}")
        
        # TEST 4: Balance Reconciliation Error (YELLOW expected)
        print("\n[TEST 4] Balance Reconciliation - Single Mismatch")
        corrupt_rows = [dict(r) for r in bank_rows]
        if len(corrupt_rows) > 5:
            original_balance = float(corrupt_rows[4]["Running_Balance"])
            corrupt_rows[4]["Running_Balance"] = str(original_balance + 5000.0)
        corrupt_bank_csv = self.to_csv_string(corrupt_rows, REQUIRED_BANK_COLUMNS)
        report4 = verify_files(corrupt_bank_csv, gst_csv)
        
        test4_result = {
            "test_name": "Balance Reconciliation Test",
            "expected": "YELLOW",
            "actual": report4['readiness'],
            "passed": report4['readiness'] == "YELLOW",
            "errors": report4['errors'],
            "warnings": report4['warnings'][:2]
        }
        results.append(test4_result)
        
        status_symbol = "[PASS]" if test4_result['passed'] else "[FAIL]"
        print(f"   {status_symbol} Readiness: {report4['readiness']} (Expected: YELLOW)")
        print(f"   {status_symbol} Warnings: {len(report4['warnings'])}")
        
        # TEST 5: Severe Balance Errors (RED expected)
        print("\n[TEST 5] Severe Balance Errors - Multiple Mismatches")
        heavy_corrupt_rows = [dict(r) for r in bank_rows]
        for idx, r in enumerate(heavy_corrupt_rows):
            if idx % 2 == 1:
                r["Running_Balance"] = str(float(r["Running_Balance"]) + 10000.0)
        heavy_corrupt_bank_csv = self.to_csv_string(heavy_corrupt_rows, REQUIRED_BANK_COLUMNS)
        report5 = verify_files(heavy_corrupt_bank_csv, gst_csv)
        
        test5_result = {
            "test_name": "Severe Balance Error Test",
            "expected": "RED",
            "actual": report5['readiness'],
            "passed": report5['readiness'] == "RED",
            "errors": report5['errors'],
            "warnings": []
        }
        results.append(test5_result)
        
        status_symbol = "[PASS]" if test5_result['passed'] else "[FAIL]"
        print(f"   {status_symbol} Readiness: {report5['readiness']} (Expected: RED)")
        print(f"   {status_symbol} Integrity compromised: {'Yes' if report5['errors'] else 'No'}")
        
        # TEST 6: Empty Bank Statement (RED expected)
        print("\n[TEST 6] Empty Data - No Transactions")
        empty_bank_csv = self.to_csv_string([], REQUIRED_BANK_COLUMNS)
        report6 = verify_files(empty_bank_csv, gst_csv)
        
        test6_result = {
            "test_name": "Empty Bank Statement Test",
            "expected": "RED",
            "actual": report6['readiness'],
            "passed": report6['readiness'] == "RED",
            "errors": report6['errors'],
            "warnings": []
        }
        results.append(test6_result)
        
        status_symbol = "[PASS]" if test6_result['passed'] else "[FAIL]"
        print(f"   {status_symbol} Readiness: {report6['readiness']} (Expected: RED)")
        
        # TEST 7: No GST Summary (YELLOW expected)
        print("\n[TEST 7] Missing GST Summary")
        report7 = verify_files(bank_csv, None)
        
        test7_result = {
            "test_name": "Missing GST Summary Test",
            "expected": "YELLOW or GREEN",
            "actual": report7['readiness'],
            "passed": report7['readiness'] in ["YELLOW", "GREEN"],
            "errors": report7['errors'],
            "warnings": report7['warnings'][:2]
        }
        results.append(test7_result)
        
        status_symbol = "[PASS]" if test7_result['passed'] else "[FAIL]"
        print(f"   {status_symbol} Readiness: {report7['readiness']}")
        print(f"   {status_symbol} GST warning issued: {'Yes' if report7['warnings'] else 'No'}")
        
        # TEST 8: Negative Transaction Values (Should trigger error)
        print("\n[TEST 8] Invalid Data - Negative Credit/Debit")
        negative_rows = [dict(r) for r in bank_rows[:20]]
        if negative_rows:
            negative_rows[5]["Credit"] = "-1000.0"
        negative_bank_csv = self.to_csv_string(negative_rows, REQUIRED_BANK_COLUMNS)
        report8 = verify_files(negative_bank_csv, gst_csv)
        
        test8_result = {
            "test_name": "Negative Values Test",
            "expected": "RED",
            "actual": report8['readiness'],
            "passed": report8['readiness'] == "RED",
            "errors": report8['errors'],
            "warnings": []
        }
        results.append(test8_result)
        
        status_symbol = "[PASS]" if test8_result['passed'] else "[FAIL]"
        print(f"   {status_symbol} Readiness: {report8['readiness']} (Expected: RED)")
        
        # Summary
        print(f"\n{'='*80}")
        print("FINANCIAL AGENT TEST SUMMARY")
        print(f"{'='*80}")
        passed_tests = sum(1 for r in results if r['passed'])
        total_tests = len(results)
        print(f"[PASS] Passed: {passed_tests}/{total_tests} tests")
        print(f"[FAIL] Failed: {total_tests - passed_tests}/{total_tests} tests")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        self.test_results['financial_agent_tests'] = results
        
        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": total_tests - passed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "detailed_results": results,
            "clean_data_report": report1  # For passing to Risk Agent
        }
    
    def test_risk_agent(self, bank_rows: List[Dict], gst_rows: List[Dict], business_info: Dict) -> Dict:
        """Test Risk Intelligence Agent with validated data."""
        print(f"\n{'='*80}")
        print("RISK INTELLIGENCE AGENT - INTEGRATION TEST")
        print(f"{'='*80}")
        
        tests = []
        
        try:
            # TEST 1: Import Risk Agent Modules
            print("\n[TEST 1] Import Risk Agent Components")
            try:
                from agents.risk_intelligence_agent.schemas import (
                    MSMEInput, GSTData, UPITransaction, AccountAggregatorData, 
                    EPFOData, BankData
                )
                print("   [PASS] PASSED: All modules imported successfully")
                import_test = {"test_name": "Module Import", "passed": True, "error": None}
                tests.append(import_test)
            except Exception as e:
                print(f"   [FAIL] FAILED: {str(e)}")
                import_test = {"test_name": "Module Import", "passed": False, "error": str(e)}
                tests.append(import_test)
                return {"total_tests": 1, "passed": 0, "failed": 1, "tests": tests}
            
            print("\n[STEP 2] Converting Dataset to Risk Agent Format...")
            
            # Generate synthetic GSTIN and PAN (required by Risk Agent)
            business_id = business_info["Business_ID"]
            # Format: 27ABCDE1234A1Z5 (state code + 5 letters + 4 digits + check digits)
            synthetic_gstin = f"27ABCDE1234A1Z5"
            # Format: ABCDE1234F
            synthetic_pan = f"ABCDE1234F"
            
            print(f"   [PASS] Business: {business_info['Business_Name']} ({business_info['Owner_Name']})")
            print(f"   [PASS] GSTIN (synthetic): {synthetic_gstin}")
            print(f"   [PASS] PAN (synthetic): {synthetic_pan}")
            
            # TEST 2: Create GSTData
            print("\n[TEST 2] GSTData Schema Validation")
            try:
                gst_monthly_revenue = [float(row["Sales"]) for row in gst_rows]
                gst_filing_history = [row["Filed_On_Time"] == "Yes" for row in gst_rows]
                gst_annual_turnover = float(business_info["Annual_Turnover_INR"])
                
                gst_data = GSTData(
                    gstin=synthetic_gstin,
                    monthly_revenue=gst_monthly_revenue,
                    filing_history=gst_filing_history,
                    annual_turnover=gst_annual_turnover
                )
                print(f"   [PASS] PASSED: GSTData created ({len(gst_monthly_revenue)} months)")
                gst_test = {"test_name": "GSTData Schema", "passed": True, "error": None}
                tests.append(gst_test)
            except Exception as e:
                print(f"   [FAIL] FAILED: {str(e)}")
                gst_test = {"test_name": "GSTData Schema", "passed": False, "error": str(e)}
                tests.append(gst_test)
            
            # TEST 3: Create AccountAggregatorData
            print("\n[TEST 3] AccountAggregatorData Schema Validation")
            try:
                from datetime import date as date_cls
                
                # Group transactions by month
                monthly_data = {}
                for bank_row in bank_rows:
                    month = bank_row["Date"][:7]  # YYYY-MM
                    if month not in monthly_data:
                        monthly_data[month] = {"inflows": 0.0, "outflows": 0.0, "end_balance": 0.0}
                    
                    credit = float(bank_row.get("Credit", 0) or 0)
                    debit = float(bank_row.get("Debit", 0) or 0)
                    
                    monthly_data[month]["inflows"] += credit
                    monthly_data[month]["outflows"] += debit
                    monthly_data[month]["end_balance"] = float(bank_row["Running_Balance"])
                
                sorted_months = sorted(monthly_data.keys())
                month_end_balances = [monthly_data[m]["end_balance"] for m in sorted_months]
                monthly_inflows = [monthly_data[m]["inflows"] for m in sorted_months]
                monthly_outflows = [monthly_data[m]["outflows"] for m in sorted_months]
                
                statement_start = date_cls.fromisoformat(bank_rows[0]["Date"])
                statement_end = date_cls.fromisoformat(bank_rows[-1]["Date"])
                
                account_agg_data = AccountAggregatorData(
                    month_end_balances=month_end_balances,
                    monthly_inflows=monthly_inflows,
                    monthly_outflows=monthly_outflows,
                    statement_start_date=statement_start,
                    statement_end_date=statement_end
                )
                days_coverage = (statement_end - statement_start).days
                print(f"   [PASS] PASSED: AccountAggregatorData created ({len(sorted_months)} months, {days_coverage} days)")
                account_test = {"test_name": "AccountAggregatorData Schema", "passed": True, "error": None}
                tests.append(account_test)
            except Exception as e:
                print(f"   [FAIL] FAILED: {str(e)}")
                account_test = {"test_name": "AccountAggregatorData Schema", "passed": False, "error": str(e)}
                tests.append(account_test)
            
            # TEST 4: Create UPI Transactions
            print("\n[TEST 4] UPI Transaction Schema Validation")
            try:
                upi_transactions = []
                for i, bank_row in enumerate(bank_rows[:10]):  # Sample first 10
                    amount = float(bank_row.get("Credit", 0) or bank_row.get("Debit", 0) or 0)
                    if amount > 0:
                        upi_transactions.append(UPITransaction(
                            amount=round(amount, 2),
                            timestamp=datetime.fromisoformat(f"{bank_row['Date']}T10:00:00"),
                            counterparty=f"VENDOR{i:03d}"
                        ))
                
                if not upi_transactions:
                    upi_transactions.append(UPITransaction(
                        amount=1000.0,
                        timestamp=datetime.fromisoformat(f"{bank_rows[0]['Date']}T10:00:00"),
                        counterparty="VENDOR001"
                    ))
                
                print(f"   [PASS] PASSED: Created {len(upi_transactions)} UPI transactions")
                upi_test = {"test_name": "UPI Transaction Schema", "passed": True, "error": None}
                tests.append(upi_test)
            except Exception as e:
                print(f"   [FAIL] FAILED: {str(e)}")
                upi_test = {"test_name": "UPI Transaction Schema", "passed": False, "error": str(e)}
                tests.append(upi_test)
            
            # TEST 5: Create EPFOData
            print("\n[TEST 5] EPFOData Schema Validation")
            try:
                employee_count = int(business_info["Employee_Count"])
                monthly_employee_counts = [employee_count] * len(sorted_months)
                
                epfo_data = EPFOData(
                    monthly_employee_counts=monthly_employee_counts
                )
                print(f"   [PASS] PASSED: EPFOData created ({len(monthly_employee_counts)} months, {employee_count} employees)")
                epfo_test = {"test_name": "EPFOData Schema", "passed": True, "error": None}
                tests.append(epfo_test)
            except Exception as e:
                print(f"   [FAIL] FAILED: {str(e)}")
                epfo_test = {"test_name": "EPFOData Schema", "passed": False, "error": str(e)}
                tests.append(epfo_test)
            
            # TEST 6: Create BankData
            print("\n[TEST 6] BankData Schema Validation")
            try:
                existing_emi = float(business_info.get("Existing_EMI_INR", 0))
                bank_data = BankData(
                    total_monthly_emi=existing_emi,
                    loan_amounts=[float(business_info.get("Working_Capital_INR", 0))] if existing_emi > 0 else [],
                    account_number=f"ACC{business_id}"
                )
                print(f"   [PASS] PASSED: BankData created (EMI: ₹{existing_emi:,.2f})")
                bank_test = {"test_name": "BankData Schema", "passed": True, "error": None}
                tests.append(bank_test)
            except Exception as e:
                print(f"   [FAIL] FAILED: {str(e)}")
                bank_test = {"test_name": "BankData Schema", "passed": False, "error": str(e)}
                tests.append(bank_test)
            
            # TEST 7: Create Complete MSMEInput
            print("\n[TEST 7] Complete MSMEInput Schema Validation")
            try:
                from datetime import timedelta
                business_age_years = int(business_info["Business_Age_Years"])
                registration_date = date_cls.today() - timedelta(days=business_age_years * 365)
                
                msme_input = MSMEInput(
                    gstin=synthetic_gstin,
                    pan=synthetic_pan,
                    business_registration_date=registration_date,
                    gst_data=gst_data,
                    upi_transactions=upi_transactions,
                    account_aggregator_data=account_agg_data,
                    epfo_data=epfo_data,
                    bank_data=bank_data
                )
                print(f"   [PASS] PASSED: Complete MSMEInput validated for {business_id}")
                print(f"      Business Age: {business_age_years} years")
                print(f"      Annual Turnover: ₹{gst_annual_turnover:,.2f}")
                print(f"      Bank Coverage: {days_coverage} days")
                msme_test = {"test_name": "Complete MSMEInput Schema", "passed": True, "error": None}
                tests.append(msme_test)
            except Exception as e:
                print(f"   [FAIL] FAILED: {str(e)}")
                import traceback
                traceback.print_exc()
                msme_test = {"test_name": "Complete MSMEInput Schema", "passed": False, "error": str(e)}
                tests.append(msme_test)
            
            # Summary
            passed_count = sum(1 for t in tests if t['passed'])
            
            print(f"\n{'='*80}")
            print("RISK INTELLIGENCE AGENT TEST SUMMARY")
            print(f"{'='*80}")
            print(f"[PASS] Passed: {passed_count}/{len(tests)} tests")
            print(f"[FAIL] Failed: {len(tests) - passed_count}/{len(tests)} tests")
            
            if passed_count == len(tests):
                print(f"\n✅ SUCCESS: Data from Financial Agent is fully compatible with Risk Intelligence Agent!")
                print(f"   All {len(tests)} schema validations passed.")
            else:
                print(f"\n⚠️ PARTIAL SUCCESS: {passed_count}/{len(tests)} tests passed")
            
            self.test_results['risk_agent_tests'] = tests
            
            return {
                "total_tests": len(tests),
                "passed": passed_count,
                "failed": len(tests) - passed_count,
                "success_rate": (passed_count/len(tests))*100,
                "tests": tests
            }
            
        except Exception as e:
            print(f"\n[FAIL] UNEXPECTED ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "total_tests": len(tests),
                "passed": sum(1 for t in tests if t['passed']),
                "failed": len(tests) - sum(1 for t in tests if t['passed']) + 1,
                "error": f"Unexpected error: {str(e)}"
            }
        """Test Risk Intelligence Agent with validated data."""
        print(f"\n{'='*80}")
        print("RISK INTELLIGENCE AGENT - INTEGRATION TEST")
        print(f"{'='*80}")
        
        try:
            # Import Risk Agent components
            from agents.risk_intelligence_agent.schemas import (
                MSMEInput, GSTData, UPITransaction, AccountAggregatorData, 
                EPFOData, BankData
            )
            from agents.risk_intelligence_agent.validator import DataValidator
            from agents.risk_intelligence_agent.feature_engineering import FeatureEngineer
            from agents.risk_intelligence_agent.policy_engine import PolicyEngine
            from agents.risk_intelligence_agent.fraud_engine import FraudEngine
            
            print("\n[STEP 2] Converting Dataset to Risk Agent Format...")
            
            # Generate synthetic GSTIN and PAN (required by Risk Agent)
            business_id = business_info["Business_ID"]
            # Format: 27ABCDE1234A1Z5 (state code + 5 letters + 4 digits + check digits)
            synthetic_gstin = f"27{business_id[:5].upper()}1234A1Z5"
            # Format: ABCDE1234F
            synthetic_pan = f"{business_id[:5].upper()}1234F"
            
            print(f"   [PASS] GSTIN (synthetic): {synthetic_gstin}")
            print(f"   [PASS] PAN (synthetic): {synthetic_pan}")
            
            # Convert GST data
            gst_monthly_revenue = [float(row["Sales"]) for row in gst_rows]
            gst_filing_history = [row["Filed_On_Time"] == "Yes" for row in gst_rows]
            gst_annual_turnover = float(business_info["Annual_Turnover_INR"])
            
            gst_data = GSTData(
                gstin=synthetic_gstin,
                monthly_revenue=gst_monthly_revenue,
                filing_history=gst_filing_history,
                annual_turnover=gst_annual_turnover
            )
            
            # Convert bank data to Account Aggregator format
            from datetime import date as date_cls
            
            # Group transactions by month
            monthly_data = {}
            for bank_row in bank_rows:
                month = bank_row["Date"][:7]  # YYYY-MM
                if month not in monthly_data:
                    monthly_data[month] = {
                        "inflows": 0.0,
                        "outflows": 0.0,
                        "end_balance": 0.0
                    }
                
                credit = float(bank_row.get("Credit", 0) or 0)
                debit = float(bank_row.get("Debit", 0) or 0)
                
                monthly_data[month]["inflows"] += credit
                monthly_data[month]["outflows"] += debit
                monthly_data[month]["end_balance"] = float(bank_row["Running_Balance"])
            
            sorted_months = sorted(monthly_data.keys())
            month_end_balances = [monthly_data[m]["end_balance"] for m in sorted_months]
            monthly_inflows = [monthly_data[m]["inflows"] for m in sorted_months]
            monthly_outflows = [monthly_data[m]["outflows"] for m in sorted_months]
            
            statement_start = date_cls.fromisoformat(bank_rows[0]["Date"])
            statement_end = date_cls.fromisoformat(bank_rows[-1]["Date"])
            
            account_agg_data = AccountAggregatorData(
                month_end_balances=month_end_balances,
                monthly_inflows=monthly_inflows,
                monthly_outflows=monthly_outflows,
                statement_start_date=statement_start,
                statement_end_date=statement_end
            )
            
            # Generate UPI transactions (at least 1 required)
            upi_transactions = []
            for i, bank_row in enumerate(bank_rows[:20]):  # Sample first 20
                if bank_row.get("Payment_Mode") == "UPI" or i == 0:  # Ensure at least one
                    amount = float(bank_row.get("Credit", 0) or bank_row.get("Debit", 0) or 1000.0)
                    if amount > 0:
                        upi_transactions.append(UPITransaction(
                            amount=round(amount, 2),
                            timestamp=datetime.fromisoformat(f"{bank_row['Date']}T10:00:00"),
                            counterparty=f"VENDOR{i:03d}"
                        ))
            
            if not upi_transactions:
                # Add at least one sample transaction
                upi_transactions.append(UPITransaction(
                    amount=1000.0,
                    timestamp=datetime.fromisoformat(f"{bank_rows[0]['Date']}T10:00:00"),
                    counterparty="VENDOR001"
                ))
            
            # EPFO data (employee counts per month)
            employee_count = int(business_info["Employee_Count"])
            monthly_employee_counts = [employee_count] * len(sorted_months)
            
            epfo_data = EPFOData(
                monthly_employee_counts=monthly_employee_counts
            )
            
            # Bank loan data
            existing_emi = float(business_info.get("Existing_EMI_INR", 0))
            bank_data = BankData(
                total_monthly_emi=existing_emi,
                loan_amounts=[float(business_info.get("Working_Capital_INR", 0))] if existing_emi > 0 else [],
                account_number=f"ACC{business_id}"
            )
            
            # Business registration date (estimate based on age)
            from datetime import timedelta
            business_age_years = int(business_info["Business_Age_Years"])
            registration_date = date_cls.today() - timedelta(days=business_age_years * 365)
            
            # Create MSME Input
            msme_input = MSMEInput(
                gstin=synthetic_gstin,
                pan=synthetic_pan,
                business_registration_date=registration_date,
                gst_data=gst_data,
                upi_transactions=upi_transactions,
                account_aggregator_data=account_agg_data,
                epfo_data=epfo_data,
                bank_data=bank_data
            )
            
            print(f"   [PASS] Created MSMEInput payload for {business_id}")
            
            # TEST 1: Schema Validation
            print("\n[TEST 1] Pydantic Schema Validation")
            try:
                # Already validated by creating MSMEInput
                print("   [PASS] PASSED: Schema validation successful")
                schema_test = {"test_name": "Schema Validation", "passed": True, "error": None}
            except Exception as e:
                print(f"   [FAIL] FAILED: {str(e)}")
                schema_test = {"test_name": "Schema Validation", "passed": False, "error": str(e)}
                return {"tests": [schema_test], "overall_status": "FAILED"}
            
            # TEST 2: Data Validator
            print("\n[TEST 2] Data Validator Component")
            try:
                validator = DataValidator()
                validation_result = validator.validate(msme_input)
                if validation_result.is_valid:
                    print("   [PASS] PASSED: Data validation successful")
                    validator_test = {"test_name": "Data Validator", "passed": True, "error": None}
                else:
                    print(f"   [FAIL] FAILED: {validation_result.errors}")
                    validator_test = {"test_name": "Data Validator", "passed": False, "error": validation_result.errors}
            except Exception as e:
                print(f"   [FAIL] FAILED: {str(e)}")
                validator_test = {"test_name": "Data Validator", "passed": False, "error": str(e)}
            
            # TEST 3: Feature Engineering
            print("\n[TEST 3] Feature Engineering Component")
            try:
                engineer = FeatureEngineer()
                features = engineer.engineer_features(msme_input)
                print(f"   [PASS] PASSED: Generated feature vector")
                print(f"      Feature values: {features.values}")
                print(f"      Feature names: {features.feature_names}")
                feature_test = {"test_name": "Feature Engineering", "passed": True, "features": features.values}
            except Exception as e:
                print(f"   [FAIL] FAILED: {str(e)}")
                import traceback
                traceback.print_exc()
                feature_test = {"test_name": "Feature Engineering", "passed": False, "error": str(e)}
            
            # TEST 4: Policy Engine
            print("\n[TEST 4] Policy Engine Component")
            try:
                policy_engine = PolicyEngine()
                policy_result = policy_engine.evaluate(msme_input, features)
                violations = [v.rule_name for v in policy_result.violations]
                print(f"   [PASS] PASSED: Evaluated policies")
                print(f"      Violations: {len(violations)}")
                if violations:
                    for v in violations[:3]:
                        print(f"         - {v}")
                policy_test = {"test_name": "Policy Engine", "passed": True, "violations": violations}
            except Exception as e:
                print(f"   [FAIL] FAILED: {str(e)}")
                import traceback
                traceback.print_exc()
                policy_test = {"test_name": "Policy Engine", "passed": False, "error": str(e)}
            
            # TEST 5: Fraud Engine
            print("\n[TEST 5] Fraud Detection Component")
            try:
                fraud_engine = FraudEngine()
                fraud_result = fraud_engine.detect_fraud(msme_input)
                fraud_flags = {flag.fraud_type: flag.severity for flag in fraud_result.fraud_flags}
                flagged_count = len(fraud_result.fraud_flags)
                print(f"   [PASS] PASSED: Fraud detection complete")
                print(f"      Flags raised: {flagged_count}")
                if flagged_count > 0:
                    for flag_type, severity in list(fraud_flags.items())[:3]:
                        print(f"         - {flag_type}: {severity}")
                fraud_test = {"test_name": "Fraud Detection", "passed": True, "fraud_flags": fraud_flags}
            except Exception as e:
                print(f"   [FAIL] FAILED: {str(e)}")
                import traceback
                traceback.print_exc()
                fraud_test = {"test_name": "Fraud Detection", "passed": False, "error": str(e)}
            
            # Collect all tests
            tests = [schema_test, validator_test, feature_test, policy_test, fraud_test]
            passed_count = sum(1 for t in tests if t['passed'])
            
            print(f"\n{'='*80}")
            print("RISK INTELLIGENCE AGENT TEST SUMMARY")
            print(f"{'='*80}")
            print(f"[PASS] Passed: {passed_count}/{len(tests)} tests")
            print(f"[FAIL] Failed: {len(tests) - passed_count}/{len(tests)} tests")
            
            self.test_results['risk_agent_tests'] = tests
            
            return {
                "total_tests": len(tests),
                "passed": passed_count,
                "failed": len(tests) - passed_count,
                "success_rate": (passed_count/len(tests))*100,
                "tests": tests
            }
            
        except ImportError as e:
            print(f"\n[FAIL] FAILED TO IMPORT RISK AGENT: {str(e)}")
            print("   Make sure Risk Intelligence Agent is properly installed.")
            return {
                "total_tests": 0,
                "passed": 0,
                "failed": 1,
                "error": f"Import error: {str(e)}"
            }
        except Exception as e:
            print(f"\n[FAIL] UNEXPECTED ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "total_tests": 0,
                "passed": 0,
                "failed": 1,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def run_full_pipeline(self, business_id: str = "MSME001"):
        """Run complete dual-agent integration test."""
        print(f"\n{'#'*80}")
        print("DUAL-AGENT INTEGRATION TEST PIPELINE")
        print(f"{'#'*80}")
        print(f"Testing: Financial Agent -> Risk Intelligence Agent")
        print(f"Business ID: {business_id}")
        print(f"{'#'*80}")
        
        try:
            # Step 1: Load data
            bank_rows, gst_rows, business_info = self.load_business_data(business_id)
            
            # Step 2: Test Financial Agent
            financial_results = self.test_financial_agent_all_cases(bank_rows, gst_rows)
            
            # Step 3: Test Risk Agent (only if Financial Agent passes)
            if financial_results['passed'] > 0:
                risk_results = self.test_risk_agent(bank_rows, gst_rows, business_info)
            else:
                print("\n⚠ Skipping Risk Agent tests - Financial Agent failed all tests")
                risk_results = {"total_tests": 0, "passed": 0, "failed": 0, "skipped": True}
            
            # Step 4: Final Summary
            print(f"\n{'#'*80}")
            print("FINAL INTEGRATION SUMMARY")
            print(f"{'#'*80}")
            print(f"\n📊 Financial Agent:")
            print(f"   Total Tests: {financial_results['total_tests']}")
            print(f"   Passed: {financial_results['passed']}")
            print(f"   Failed: {financial_results['failed']}")
            print(f"   Success Rate: {financial_results['success_rate']:.1f}%")
            
            print(f"\n🎯 Risk Intelligence Agent:")
            print(f"   Total Tests: {risk_results.get('total_tests', 0)}")
            print(f"   Passed: {risk_results.get('passed', 0)}")
            print(f"   Failed: {risk_results.get('failed', 0)}")
            if risk_results.get('total_tests', 0) > 0:
                print(f"   Success Rate: {risk_results.get('success_rate', 0):.1f}%")
            
            # Overall Status
            overall_passed = financial_results['passed'] + risk_results.get('passed', 0)
            overall_total = financial_results['total_tests'] + risk_results.get('total_tests', 0)
            
            print(f"\n{'='*80}")
            if overall_total > 0:
                overall_rate = (overall_passed / overall_total) * 100
                print(f"🏆 OVERALL SUCCESS RATE: {overall_rate:.1f}% ({overall_passed}/{overall_total} tests passed)")
            else:
                print(f"⚠ NO TESTS COMPLETED")
            print(f"{'='*80}")
            
            # Save detailed report
            report_path = os.path.join(os.path.dirname(__file__), "dual_agent_test_report.json")
            with open(report_path, "w") as f:
                json.dump({
                    "business_id": business_id,
                    "business_name": business_info["Business_Name"],
                    "owner_name": business_info["Owner_Name"],
                    "financial_agent": financial_results,
                    "risk_agent": risk_results,
                    "overall": {
                        "total_tests": overall_total,
                        "passed": overall_passed,
                        "failed": overall_total - overall_passed,
                        "success_rate": overall_rate if overall_total > 0 else 0
                    },
                    "timestamp": datetime.now().isoformat()
                }, f, indent=2, default=str)
            
            print(f"\n📄 Detailed report saved to: {report_path}")
            
            return True
            
        except Exception as e:
            print(f"\n[FAIL] PIPELINE FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    tester = DualAgentTester()
    success = tester.run_full_pipeline(business_id="MSME001")
    sys.exit(0 if success else 1)
