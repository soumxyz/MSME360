import os
import json
import random
from datetime import datetime, timedelta

def rand_str(length=5):
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "".join(random.choice(chars) for _ in range(length))

def rand_digits(length=4):
    chars = "0123456789"
    return "".join(random.choice(chars) for _ in range(length))

def generate_profile(idx):
    gstin = f"27{rand_str(5)}{rand_digits(4)}A1Z5"
    pan = f"{rand_str(5)}{rand_digits(4)}F"
    
    # 12 months of revenues
    # Mix of low, mid, high, and volatile revenues
    risk_profile = random.choice(["low", "medium", "high", "volatile"])
    
    if risk_profile == "low":
        rev_base = random.randint(500000, 1000000)
        revenues = [rev_base * random.uniform(0.9, 1.1) for _ in range(12)]
        filings = [True] * 12 # Perfect GST filings
        balances = [rev_base * random.uniform(0.2, 0.4) for _ in range(12)]
        inflows = revenues[:]
        outflows = [inflows[i] * random.uniform(0.7, 0.8) for i in range(12)]
    elif risk_profile == "medium":
        rev_base = random.randint(300000, 600000)
        revenues = [rev_base * random.uniform(0.8, 1.2) for _ in range(12)]
        filings = [True] * 10 + [False] * 2 # Missed 2 filings
        balances = [rev_base * random.uniform(0.1, 0.25) for _ in range(12)]
        inflows = revenues[:]
        outflows = [inflows[i] * random.uniform(0.8, 0.9) for i in range(12)]
    elif risk_profile == "high":
        rev_base = random.randint(100000, 300000)
        revenues = [rev_base * random.uniform(0.6, 1.3) for _ in range(12)]
        filings = [True] * 8 + [False] * 4 # Missed 4 filings
        balances = [rev_base * random.uniform(0.02, 0.1) for _ in range(12)]
        inflows = revenues[:]
        outflows = [inflows[i] * random.uniform(0.9, 0.98) for i in range(12)]
    else: # Volatile (fraud indicator or high risk)
        rev_base = random.randint(200000, 800000)
        # Extreme revenue spikes or sudden drops
        revenues = [rev_base * (5.0 if i == 5 else random.uniform(0.5, 1.5)) for i in range(12)]
        filings = [True] * 11 + [False] * 1
        balances = [rev_base * random.uniform(0.01, 0.5) for _ in range(12)]
        inflows = revenues[:]
        outflows = [inflows[i] * random.uniform(0.7, 0.95) for i in range(12)]

    # Dynamic dates
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365)
    
    # EPFO
    emp_count = random.randint(2, 25)
    epfo_counts = [emp_count + random.choice([-1, 0, 1]) for _ in range(12)]
    epfo_counts = [max(1, count) for count in epfo_counts]
    
    # UPI
    upi_txns = []
    for day in range(1, 30, 3):
        upi_txns.append({
            "amount": round(random.uniform(500.0, 5000.0), 2),
            "timestamp": (datetime.now() - timedelta(days=day)).isoformat(),
            "counterparty": f"Vendor {rand_str(3)}"
        })

    # Bank data
    has_existing_loans = random.choice([True, False])
    emi = round(random.uniform(10000.0, 50000.0), 2) if has_existing_loans else 0.0
    loan_amounts = [float(random.randint(100000, 500000))] if has_existing_loans else []

    return {
        "msme_id": f"MSME_TEST_{idx:03d}",
        "pan": pan,
        "gstin": gstin,
        "business_registration_date": (datetime.now().date() - timedelta(days=365 * random.randint(2, 15))).isoformat(),
        "gst_data": {
            "gstin": gstin,
            "monthly_revenue": [round(r, 2) for r in revenues],
            "filing_history": filings,
            "annual_turnover": round(sum(revenues), 2)
        },
        "upi_transactions": upi_txns,
        "account_aggregator_data": {
            "month_end_balances": [round(b, 2) for b in balances],
            "monthly_inflows": [round(i, 2) for i in inflows],
            "monthly_outflows": [round(o, 2) for o in outflows],
            "statement_start_date": start_date.isoformat(),
            "statement_end_date": end_date.isoformat()
        },
        "epfo_data": {
            "monthly_employee_counts": epfo_counts
        },
        "bank_data": {
            "total_monthly_emi": emi,
            "loan_amounts": loan_amounts,
            "account_number": f"919{rand_digits(9)}"
        }
    }

def main():
    print("Generating 120 synthetic test cases...")
    test_cases = [generate_profile(i) for i in range(1, 121)]
    
    os.makedirs("tests", exist_ok=True)
    with open("tests/synthetic_msmes.json", "w") as f:
        json.dump(test_cases, f, indent=2)
        
    print(f"[SUCCESS] Wrote 120 test cases to 'tests/synthetic_msmes.json'")

if __name__ == "__main__":
    main()
