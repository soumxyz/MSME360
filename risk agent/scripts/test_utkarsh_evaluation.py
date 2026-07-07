import os
import json
import csv
import asyncio
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.risk_intelligence_agent.workflow import evaluate_msme
from agents.risk_intelligence_agent.schemas import MSMEInput, GSTData, AccountAggregatorData, UPITransaction, EPFOData, BankData
from datetime import datetime, date

async def test_utkarsh_evaluation():
    print("========================================================================")
    print("RUNNING END-TO-END VERIFICATION FOR UTKARSH SINHA IDBI APPLICATION")
    print("========================================================================")

    data_dir = Path("/Users/utkarshsinha/Desktop/MSME360/risk agent/data/utkarsh_sinha")
    
    # 1. Load Aadhaar & PAN
    with open(data_dir / "aadhaar.json", "r") as f:
        aadhaar = json.load(f)
    with open(data_dir / "pan.json", "r") as f:
        pan = json.load(f)

    print(f"[INFO] Loaded identity data: Name: {aadhaar['name']}, PAN: {pan['pan']}")

    # 2. Parse GST Returns
    gst_returns = []
    gst_gross_turnover = 0.0
    gst_filing_history = []
    
    with open(data_dir / "gst_summary.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            gst_returns.append(float(row["Gross_Turnover"]))
            gst_gross_turnover += float(row["Gross_Turnover"])
            gst_filing_history.append(row["Filing_Status"] == "Filed")

    print(f"[INFO] Parsed GST records: Total Turnover: ₹{gst_gross_turnover:.2f}, Months count: {len(gst_returns)}")

    # 3. Parse Bank Transactions (from CSV)
    balances = []
    inflows = []
    outflows = []
    upi_txs = []
    
    with open(data_dir / "bank_transactions.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            running_balance = float(row["Running_Balance"])
            debit = float(row["Debit_Amount"])
            credit = float(row["Credit_Amount"])
            balances.append(running_balance)
            if credit > 0:
                inflows.append(credit)
            if debit > 0:
                outflows.append(debit)
            
            # Map upi transaction objects
            upi_txs.append(UPITransaction(
                amount=credit if credit > 0 else debit,
                timestamp=datetime.strptime(row["Date"] + " 10:00:00", "%Y-%m-%d %H:%M:%S"),
                counterparty=row["Description"]
            ))

    print(f"[INFO] Parsed Bank records: Transactions count: {len(balances)}, Avg Running Balance: ₹{sum(balances)/len(balances):.2f}")

    # Build Pydantic inputs matching schemas
    gst_data = GSTData(
        gstin="27UTKPS2849S1ZH",
        monthly_revenue=gst_returns,
        filing_history=gst_filing_history,
        annual_turnover=gst_gross_turnover
    )

    aa_data = AccountAggregatorData(
        month_end_balances=[balances[0], balances[len(balances)//2], balances[-1]],
        monthly_inflows=[sum(inflows)/6] * 6,
        monthly_outflows=[sum(outflows)/6] * 6,
        statement_start_date=date(2026, 1, 1),
        statement_end_date=date(2026, 6, 30)
    )

    epfo_data = EPFOData(
        monthly_employee_counts=[18] * 12
    )

    bank_data = BankData(
        total_monthly_emi=42000.0,
        loan_amounts=[1500000.0],
        account_number="IDBI-UTK-829310"
    )

    msme_input = MSMEInput(
        gstin="27UTKPS2849S1ZH",
        pan=pan["pan"],
        business_registration_date=date(2022, 1, 15),
        gst_data=gst_data,
        upi_transactions=upi_txs[:50], # Take first 50 transactions to satisfy size bounds
        account_aggregator_data=aa_data,
        epfo_data=epfo_data,
        bank_data=bank_data
    )

    # 4. Trigger evaluation flow
    print("\n--- Executing real-time credit agent workflow evaluation ---")
    
    report = await evaluate_msme(msme_input)

    if report:
        print("\n========================================================================")
        print("VERIFICATION COMPLETED SUCCESSFULLY!")
        print("========================================================================")
        print(f"Risk Score: {report.risk_score:.2f}")
        print(f"Risk Category: {report.risk_category}")
        print(f"Recommendation: {report.recommendation}")
        print(f"Eligibility Status: {report.eligibility}")
        print(f"Confidence Level: {report.confidence_level:.2f}%")
        print(f"Financial Health Score: {report.financial_health_score:.2f}/100")
        print("\n--- Gemini Credit Memo Narrative Summary ---")
        print(report.explanation)
        
        # Assertions to ensure standard loan criteria is passed
        assert report.eligibility is True, "Utkarsh's high-credit application should be eligible"
        assert report.risk_score < 40.0, "Risk score should be low or medium due to consistent balances"
        
        print("\n[PASS] E2E Loan assessment validation tests succeeded!")
    else:
        print("\n[FAIL] Workflow failed to generate an assessment report.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_utkarsh_evaluation())
