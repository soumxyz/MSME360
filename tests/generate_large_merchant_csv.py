import pandas as pd
import random
from datetime import datetime, timedelta

def generate_large_merchant_csv():
    # Mid-sized Indian FMCG Distributor / Wholesaler
    # Spans 18 months (Jan 1, 2024 to June 30, 2025)
    # High-frequency daily trades, generating 1000+ transaction rows
    
    current_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 6, 30)
    balance = 250000.0 # Starting balance in INR
    
    rows = []
    tx_id_counter = 50001
    
    inflow_descriptions = [
        "UPI-BharatPe-Bulk-Settlement",
        "IMPS-INW-Merchant Settlement",
        "NEFT-INW-Supermarket Distributor Payout",
        "RTGS-INW-Regional Sub-Stockist",
        "Cash Deposit-Bulk-Guwahati Main Branch",
        "UPI-GPay-Merchant-Daily-Payout",
        "UPI-PhonePe-Corporate-Settlement"
    ]
    
    outflow_descriptions = [
        "RTGS-OUT-NESTLE INDIA DISTRIBUTOR",
        "NEFT-OUT-AMUL DAIRY PRODUCTS",
        "CHQ-OUT-PEPSICO INDIA HOLDINGS",
        "CHQ-OUT-COCA COLA BEVERAGES",
        "UPI-OUT-Shop Warehouse Rent",
        "UPI-OUT-Local Transport Charges",
        "IMPS-OUT-Staff Salary Disbursal",
        "Cash Withdraw-ATM-Self",
        "UPI-OUT-Customs & Octroi Duty Guwahati"
    ]
    
    # 18 months is 547 days. Generating 2 to 4 transactions per day will easily result in 1,200 to 2,000 rows.
    while current_date <= end_date:
        day_transactions = random.randint(2, 4)
        
        for _ in range(day_transactions):
            tx_id = f"TXN{tx_id_counter}"
            tx_id_counter += 1
            
            is_credit = random.choices([True, False], weights=[0.60, 0.40])[0]
            
            if is_credit:
                desc = random.choice(inflow_descriptions)
                # Larger B2B distributor receipts ranging from ₹15,000 to ₹75,000
                if "Cash Deposit" in desc or "RTGS" in desc:
                    credit = float(random.randint(50000, 150000))
                else:
                    credit = float(random.randint(10000, 45000))
                debit = 0.0
                balance += credit
            else:
                desc = random.choice(outflow_descriptions)
                credit = 0.0
                # Larger logistics & inventory payouts
                if "RTGS" in desc or "NESTLE" in desc or "AMUL" in desc or "PEPSICO" in desc:
                    debit = float(random.randint(40000, 120000))
                elif "Rent" in desc:
                    debit = 35000.0 # Warehouse rent
                elif "Salary" in desc:
                    debit = 60000.0 # Employee payroll
                else:
                    debit = float(random.randint(3000, 15000))
                
                # Check if buffer is safe
                if balance - debit > 10000:
                    balance -= debit
                else:
                    debit = float(random.randint(2000, 8000))
                    balance -= debit
                    
            rows.append({
                "Date": current_date.strftime("%Y-%m-%d"),
                "Description": desc,
                "Credit": round(credit, 2),
                "Debit": round(debit, 2),
                "Running_Balance": round(balance, 2)
            })
            
        current_date += timedelta(days=1)
        
    df = pd.DataFrame(rows)
    df.to_csv("large_indian_distributor_1500_rows.csv", index=False)
    print(f"[SUCCESS] Generated {len(df)} rows in 'large_indian_distributor_1500_rows.csv'")

if __name__ == "__main__":
    generate_large_merchant_csv()
