import pandas as pd
import random
from datetime import datetime, timedelta

def generate_indian_merchant_csv():
    # Small Indian Retailer (Kirana / General Store)
    # Spans 6 months (Jan 1, 2025 to July 5, 2025)
    # Consistent UPI settlement inflows, cash deposits, and supplier payouts (HUL, Britannia, etc.)
    
    current_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 7, 5)
    balance = 45000.0 # Starting balance in INR
    
    rows = []
    
    # Let's generate daily activity
    tx_id_counter = 10001
    
    indian_descriptions_in = [
        "UPI-PhonePe-Merchant-Settlement",
        "UPI-GPay-Retail-Settlement",
        "UPI-Paytm-Store-Payout",
        "UPI-BharatPe-POS-Settlement",
        "Cash Deposit-Self-Guwahati Branch",
        "IMPS-INW-Interest Credit",
        "NEFT-INW-B2B Retail Client"
    ]
    
    indian_descriptions_out = [
        "CHQ-OUT-HINDUSTAN UNILEVER LTD",
        "IMPS-OUT-BRITANNIA INDUSTRIES",
        "CHQ-OUT-PARLE PRODUCTS PVT LTD",
        "UPI-OUT-Electricity APDCL",
        "UPI-OUT-Shop Rent Settlement",
        "IMPS-OUT-ITC Limited Supplier",
        "Cash Withdraw-ATM-Self",
        "UPI-OUT-GPay Supplier Payment",
        "UPI-OUT-PhonePe Vendor Payout"
    ]
    
    while current_date <= end_date:
        # Kirana stores have multiple transactions every day
        # Typically 1 to 3 credit settlements (PhonePe, GPay, BharatPe) 
        # and occasional debit payouts to suppliers
        
        day_transactions = random.randint(1, 3)
        for _ in range(day_transactions):
            tx_id = f"TXN{tx_id_counter}"
            tx_id_counter += 1
            
            # Determine transaction type (weighted towards credits for settlements, but debits for inventory)
            is_credit = random.choices([True, False], weights=[0.65, 0.35])[0]
            
            if is_credit:
                desc = random.choice(indian_descriptions_in)
                # Small daily retail settlements ranging from ₹1,500 to ₹12,000
                if "Cash Deposit" in desc:
                    credit = float(random.randint(10000, 30000))
                else:
                    credit = float(random.randint(1500, 9500))
                debit = 0.0
                balance += credit
            else:
                desc = random.choice(indian_descriptions_out)
                credit = 0.0
                # Supplier invoices are larger payouts, utility bills are smaller
                if "Supplier" in desc or "HINDUSTAN" in desc or "BRITANNIA" in desc:
                    debit = float(random.randint(8000, 22000))
                elif "Rent" in desc:
                    debit = 15000.0 # Standard shop rent
                else:
                    debit = float(random.randint(1000, 5000))
                    
                # To prevent balance going negative, check if we have enough buffer
                if balance - debit > 2000:
                    balance -= debit
                else:
                    # Fallback to a very small debit or skip
                    debit = float(random.randint(500, 1500))
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
    df.to_csv("indian_kirana_medium_risk.csv", index=False)
    print(f"[SUCCESS] Generated {len(df)} rows of Indian Kirana store transactions in 'indian_kirana_medium_risk.csv'")

if __name__ == "__main__":
    generate_indian_merchant_csv()
