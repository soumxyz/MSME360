import os
import json
import csv
from datetime import datetime, timedelta

def generate_dataset():
    target_dir = "/Users/utkarshsinha/Desktop/MSME360/risk agent/data/utkarsh_sinha"
    os.makedirs(target_dir, exist_ok=True)

    # 1. Generate Aadhaar
    aadhaar_data = {
        "name": "Utkarsh Sinha",
        "aadhaar_number": "XXXX-XXXX-4829",
        "dob": "1995-05-12",
        "gender": "MALE",
        "address": "Flat 402, Green Glen Layout, Outer Ring Road, Bangalore, Karnataka - 560103"
    }
    with open(os.path.join(target_dir, "aadhaar.json"), "w") as f:
        json.dump(aadhaar_data, f, indent=2)

    # 2. Generate PAN
    pan_data = {
        "pan": "UTKPS2849S",
        "name": "Utkarsh Sinha",
        "dob": "1995-05-12",
        "status": "ACTIVE",
        "category": "INDIVIDUAL"
    }
    with open(os.path.join(target_dir, "pan.json"), "w") as f:
        json.dump(pan_data, f, indent=2)

    # 3. Generate GST Summary CSV for Agent 1
    gst_columns = ["Business_ID", "GSTIN", "Filing_Period", "Gross_Turnover", "Filing_Status", "Filing_Date"]
    gst_rows = []
    start_date = datetime(2025, 7, 1)
    for i in range(12):
        period_date = start_date + timedelta(days=i*30)
        period_str = period_date.strftime("%Y-%m")
        gst_rows.append({
            "Business_ID": "MSME_UTKARSH",
            "GSTIN": "27UTKPS2849S1ZH",
            "Filing_Period": period_str,
            "Gross_Turnover": str(520000.0 + (i * 15000.0)), # Growth trend
            "Filing_Status": "Filed",
            "Filing_Date": (period_date + timedelta(days=12)).strftime("%Y-%m-%d")
        })
    
    with open(os.path.join(target_dir, "gst_summary.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=gst_columns)
        writer.writeheader()
        writer.writerows(gst_rows)

    # 4. Generate Bank Transactions CSV for Agent 1 (with perfect running balance math)
    bank_columns = ["Business_ID", "Transaction_ID", "Date", "Description", "Debit_Amount", "Credit_Amount", "Running_Balance"]
    bank_rows = []
    balance = 1200000.0 # Initial balance
    
    start_bank = datetime(2026, 1, 1)
    for idx in range(180): # 180 days of transactions (6 months coverage)
        tx_date = start_bank + timedelta(days=idx)
        
        # Credit transaction (sales inflow) every 3 days
        if idx % 3 == 0:
            credit = 45000.0
            debit = 0.0
            balance += credit
            bank_rows.append({
                "Business_ID": "MSME_UTKARSH",
                "Transaction_ID": f"TXN-UTK-{idx:05d}",
                "Date": tx_date.strftime("%Y-%m-%d"),
                "Description": "UPI SALES MERCHANT CR",
                "Debit_Amount": str(debit),
                "Credit_Amount": str(credit),
                "Running_Balance": f"{balance:.2f}"
            })
        
        # Debit transaction (operational expenses) every 5 days
        if idx % 5 == 0:
            credit = 0.0
            debit = 18000.0
            balance -= debit
            bank_rows.append({
                "Business_ID": "MSME_UTKARSH",
                "Transaction_ID": f"TXN-UTK-{idx:05d}-DR",
                "Date": tx_date.strftime("%Y-%m-%d"),
                "Description": "VENDOR ONLINE OUTFLOW DR",
                "Debit_Amount": str(debit),
                "Credit_Amount": str(credit),
                "Running_Balance": f"{balance:.2f}"
            })

    with open(os.path.join(target_dir, "bank_transactions.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=bank_columns)
        writer.writeheader()
        writer.writerows(bank_rows)

    print(f"Dataset generated successfully in {target_dir}")

if __name__ == "__main__":
    generate_dataset()
