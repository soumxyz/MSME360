"""Convert GitHub Dataset CSV files to API-compatible JSON format.

This script reads the CSV files from the Dataset folder and converts them
into the MSMEInput format expected by the Risk Intelligence Agent API.
"""

import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Dataset paths
DATASET_ROOT = Path("/Users/utkarshsinha/Desktop/MSME360/Dataset")
OUTPUT_DIR = Path("/Users/utkarshsinha/Desktop/MSME360/risk agent/data/converted")


def load_dataset():
    """Load all CSV files from the Dataset folder."""
    print("Loading dataset files...")
    
    data = {}
    
    # Load businesses
    businesses_path = DATASET_ROOT / "businesses.csv"
    if businesses_path.exists():
        data['businesses'] = pd.read_csv(businesses_path)
        print(f"✅ Loaded businesses: {len(data['businesses'])} records")
    
    # Load GST summary
    gst_path = DATASET_ROOT / "gst_summary.csv"
    if gst_path.exists():
        data['gst_summary'] = pd.read_csv(gst_path)
        print(f"✅ Loaded GST summary: {len(data['gst_summary'])} records")
    
    # Load bank transactions
    bank_path = DATASET_ROOT / "bank_transactions.csv"
    if bank_path.exists():
        data['bank_transactions'] = pd.read_csv(bank_path)
        print(f"✅ Loaded bank transactions: {len(data['bank_transactions'])} records")
    
    # Load credit labels
    credit_path = DATASET_ROOT / "credit_labels.csv"
    if credit_path.exists():
        data['credit_labels'] = pd.read_csv(credit_path)
        print(f"✅ Loaded credit labels: {len(data['credit_labels'])} records")
    
    # Load engineered features
    features_path = DATASET_ROOT / "engineered_features.csv"
    if features_path.exists():
        data['engineered_features'] = pd.read_csv(features_path)
        print(f"✅ Loaded engineered features: {len(data['engineered_features'])} records")
    
    return data


def convert_business_to_msme_input(business_id, dataset):
    """Convert a business record to MSMEInput format."""
    
    # Get business info
    businesses = dataset['businesses']
    business = businesses[businesses['business_id'] == business_id].iloc[0]
    
    # Get GST data
    gst_data = dataset['gst_summary'][dataset['gst_summary']['business_id'] == business_id]
    
    # Get bank transactions
    bank_txns = dataset['bank_transactions'][dataset['bank_transactions']['business_id'] == business_id]
    
    # Create MSMEInput structure
    msme_input = {
        "msme_id": str(business_id),
        "pan": business.get('pan', 'ABCDE1234F'),
        "gst_data": {
            "gstin": business.get('gstin', '27ABCDE1234F1Z5'),
            "registration_date": business.get('registration_date', '2022-01-15'),
            "monthly_returns": [],
            "filing_history": {
                "total_filings_due": int(business.get('total_filings_due', 12)),
                "filings_completed": int(business.get('filings_completed', 12)),
                "filings_missed": int(business.get('filings_missed', 0))
            }
        },
        "upi_data": {
            "transactions": [],
            "summary": {
                "total_transactions": 0,
                "total_volume": 0.0,
                "period_start": "2024-01-01",
                "period_end": "2024-12-31"
            }
        },
        "account_aggregator_data": {
            "monthly_statements": []
        },
        "epfo_data": {
            "monthly_records": []
        },
        "bank_data": {
            "monthly_emi": float(business.get('monthly_emi', 0)),
            "outstanding_loan": float(business.get('outstanding_loan', 0)),
            "loan_to_turnover_ratio": float(business.get('loan_to_turnover_ratio', 0)),
            "statement_start_date": "2024-01-01",
            "statement_end_date": "2024-12-31"
        }
    }
    
    # Add GST monthly returns
    for _, row in gst_data.iterrows():
        msme_input["gst_data"]["monthly_returns"].append({
            "month": str(row.get('month', '2024-01')),
            "revenue": float(row.get('revenue', 0)),
            "filed": bool(row.get('filed', True))
        })
    
    # Add bank transactions as UPI data (simplified)
    upi_transactions = []
    for _, row in bank_txns.head(50).iterrows():  # Limit to 50 transactions
        upi_transactions.append({
            "transaction_id": f"TXN_{row.get('transaction_id', 'UNKNOWN')}",
            "timestamp": str(row.get('transaction_date', '2024-01-01T00:00:00Z')),
            "amount": float(row.get('amount', 0)),
            "counterparty": str(row.get('counterparty', 'UNKNOWN')),
            "type": str(row.get('transaction_type', 'credit'))
        })
    
    msme_input["upi_data"]["transactions"] = upi_transactions
    msme_input["upi_data"]["summary"]["total_transactions"] = len(upi_transactions)
    msme_input["upi_data"]["summary"]["total_volume"] = sum(t['amount'] for t in upi_transactions)
    
    # Add account aggregator data (derived from bank transactions)
    monthly_balances = bank_txns.groupby('month').agg({
        'amount': 'sum',
        'transaction_id': 'count'
    }).reset_index()
    
    for _, row in monthly_balances.iterrows():
        msme_input["account_aggregator_data"]["monthly_statements"].append({
            "month": str(row['month']),
            "opening_balance": 100000.0,  # Placeholder
            "closing_balance": 100000.0 + float(row['amount']),
            "total_credits": float(row['amount']) if row['amount'] > 0 else 0,
            "total_debits": float(-row['amount']) if row['amount'] < 0 else 0
        })
    
    # Add EPFO data (simplified)
    employee_count = int(business.get('employee_count', 10))
    for i in range(12):
        month = f"2024-{i+1:02d}"
        msme_input["epfo_data"]["monthly_records"].append({
            "month": month,
            "employee_count": employee_count
        })
    
    return msme_input


def convert_all_businesses(dataset, limit=10):
    """Convert all businesses to MSMEInput format."""
    print(f"\nConverting businesses to MSMEInput format...")
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Get unique business IDs
    business_ids = dataset['businesses']['business_id'].unique()[:limit]
    
    converted = []
    for business_id in business_ids:
        try:
            msme_input = convert_business_to_msme_input(business_id, dataset)
            
            # Save to file
            output_file = OUTPUT_DIR / f"msme_{business_id}.json"
            with open(output_file, 'w') as f:
                json.dump(msme_input, f, indent=2)
            
            converted.append(business_id)
            print(f"✅ Converted business {business_id} -> {output_file.name}")
            
        except Exception as e:
            print(f"❌ Failed to convert business {business_id}: {e}")
    
    print(f"\n✅ Converted {len(converted)} businesses")
    return converted


def create_sample_files(dataset):
    """Create sample files for different scenarios."""
    print("\nCreating sample files...")
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Get businesses with different credit labels
    credit_labels = dataset.get('credit_labels')
    
    if credit_labels is not None:
        # Good credit business
        good_credit = credit_labels[credit_labels['credit_risk'] == 'low'].head(1)
        if not good_credit.empty:
            business_id = good_credit.iloc[0]['business_id']
            msme_input = convert_business_to_msme_input(business_id, dataset)
            with open(OUTPUT_DIR / "good_credit_example.json", 'w') as f:
                json.dump(msme_input, f, indent=2)
            print(f"✅ Created good_credit_example.json")
        
        # High risk business
        high_risk = credit_labels[credit_labels['credit_risk'] == 'high'].head(1)
        if not high_risk.empty:
            business_id = high_risk.iloc[0]['business_id']
            msme_input = convert_business_to_msme_input(business_id, dataset)
            with open(OUTPUT_DIR / "high_risk_example.json", 'w') as f:
                json.dump(msme_input, f, indent=2)
            print(f"✅ Created high_risk_example.json")


def generate_dataset_summary(dataset):
    """Generate a summary of the dataset."""
    summary_path = OUTPUT_DIR / "DATASET_SUMMARY.md"
    
    with open(summary_path, 'w') as f:
        f.write("# Dataset Summary\n\n")
        f.write("## Overview\n\n")
        f.write("This dataset was imported from the GitHub repository main branch.\n\n")
        
        f.write("## Files\n\n")
        for name, df in dataset.items():
            f.write(f"### {name}\n")
            f.write(f"- Records: {len(df)}\n")
            f.write(f"- Columns: {', '.join(df.columns)}\n\n")
        
        f.write("## Converted Files\n\n")
        f.write(f"Location: `{OUTPUT_DIR}`\n\n")
        f.write("The CSV data has been converted to MSMEInput JSON format compatible with the Risk Intelligence Agent API.\n\n")
        
        f.write("## Usage\n\n")
        f.write("```bash\n")
        f.write("# Test with converted data\n")
        f.write("curl -X POST http://localhost:8000/api/v1/evaluate \\\n")
        f.write("  -H \"Content-Type: application/json\" \\\n")
        f.write("  -H \"Authorization: Bearer test_token\" \\\n")
        f.write("  -d @data/converted/msme_001.json\n")
        f.write("```\n")
    
    print(f"✅ Created dataset summary: {summary_path}")


def main():
    """Main conversion function."""
    print("=" * 70)
    print("GitHub Dataset Conversion to API Format")
    print("=" * 70)
    print()
    
    # Load dataset
    dataset = load_dataset()
    
    if not dataset:
        print("\n❌ No dataset files found!")
        return
    
    print()
    
    # Convert businesses
    converted = convert_all_businesses(dataset, limit=10)
    
    # Create sample files
    create_sample_files(dataset)
    
    # Generate summary
    generate_dataset_summary(dataset)
    
    print()
    print("=" * 70)
    print("✅ Conversion Complete!")
    print("=" * 70)
    print()
    print(f"Converted files location: {OUTPUT_DIR}")
    print(f"Total files created: {len(list(OUTPUT_DIR.glob('*.json')))}")
    print()
    print("Test with converted data:")
    print("  python data/data_loader.py")


if __name__ == "__main__":
    main()
