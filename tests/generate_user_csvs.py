import pandas as pd
from datetime import datetime, timedelta

def generate_passing_csv():
    # 12 months, 180+ transactions, 0 drift
    rows = []
    current_date = datetime(2025, 1, 1)
    balance = 100000.0
    
    # 200 transactions (approx 16 per month)
    for i in range(1, 201):
        current_date += timedelta(days=1.8)
        
        # Alternate credit and debit
        if i % 2 == 1:
            credit = 25000.0
            debit = 0.0
            balance += credit
        else:
            credit = 0.0
            debit = 18000.0
            balance -= debit
            
        rows.append({
            "Date": current_date.strftime("%Y-%m-%d"),
            "Credit": credit,
            "Debit": debit,
            "Running_Balance": balance
        })
        
    df = pd.DataFrame(rows)
    df.to_csv("pass_compliance_high_score.csv", index=False)
    print("[SUCCESS] Wrote 'pass_compliance_high_score.csv'")

def generate_failing_csv():
    # covers only 1 month (fails coverage), 10 transactions, has drift anomalies
    rows = []
    current_date = datetime(2025, 1, 1)
    balance = 50000.0
    
    for i in range(1, 11):
        current_date += timedelta(days=2.5)
        
        if i % 2 == 1:
            credit = 10000.0
            debit = 0.0
            # Reconciled expected balance = balance + 10000
            # We introduce a drift by setting a wrong Running_Balance
            balance = balance + credit + (500.0 if i == 5 else 0.0)
        else:
            credit = 0.0
            debit = 8000.0
            balance = balance - debit
            
        rows.append({
            "Date": current_date.strftime("%Y-%m-%d"),
            "Credit": credit,
            "Debit": debit,
            "Running_Balance": balance
        })
        
    df = pd.DataFrame(rows)
    df.to_csv("fail_compliance_low_score.csv", index=False)
    print("[SUCCESS] Wrote 'fail_compliance_low_score.csv'")

if __name__ == "__main__":
    generate_passing_csv()
    generate_failing_csv()
