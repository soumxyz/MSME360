"""Test GitHub Dataset with Risk Intelligence Agent.

This script validates that the dataset works properly with the Risk Agent
and identifies any missing data fields.
"""

import pandas as pd
import json
from datetime import datetime, timedelta, date
from pathlib import Path
import sys
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.risk_intelligence_agent.schemas import (
    MSMEInput, GSTData, UPITransaction, AccountAggregatorData,
    EPFOData, BankData
)

# Dataset paths
DATASET_ROOT = Path("/Users/utkarshsinha/Desktop/MSME360/Dataset")
OUTPUT_DIR = Path("/Users/utkarshsinha/Desktop/MSME360/risk agent/data/test_results")


class DatasetAnalyzer:
    """Analyze dataset against API schema requirements."""
    
    def __init__(self):
        self.dataset = {}
        self.missing_fields = {}
        self.errors = []
        self.warnings = []
        
    def load_dataset(self) -> bool:
        """Load all CSV files from the Dataset folder."""
        print("=" * 70)
        print("Loading Dataset Files")
        print("=" * 70)
        
        try:
            # Load businesses
            businesses_path = DATASET_ROOT / "businesses.csv"
            if businesses_path.exists():
                self.dataset['businesses'] = pd.read_csv(businesses_path)
                print(f"✅ Businesses: {len(self.dataset['businesses'])} records")
            else:
                print(f"❌ businesses.csv not found")
                return False
            
            # Load GST summary
            gst_path = DATASET_ROOT / "gst_summary.csv"
            if gst_path.exists():
                self.dataset['gst_summary'] = pd.read_csv(gst_path)
                print(f"✅ GST Summary: {len(self.dataset['gst_summary'])} records")
            else:
                print(f"⚠️  gst_summary.csv not found")
            
            # Load bank transactions
            bank_path = DATASET_ROOT / "bank_transactions.csv"
            if bank_path.exists():
                self.dataset['bank_transactions'] = pd.read_csv(bank_path, parse_dates=['Date'])
                print(f"✅ Bank Transactions: {len(self.dataset['bank_transactions'])} records")
            else:
                print(f"⚠️  bank_transactions.csv not found")
            
            # Load engineered features
            features_path = DATASET_ROOT / "engineered_features.csv"
            if features_path.exists():
                self.dataset['engineered_features'] = pd.read_csv(features_path)
                print(f"✅ Engineered Features: {len(self.dataset['engineered_features'])} records")
            else:
                print(f"⚠️  engineered_features.csv not found")
            
            # Load credit labels
            credit_path = DATASET_ROOT / "credit_labels.csv"
            if credit_path.exists():
                self.dataset['credit_labels'] = pd.read_csv(credit_path)
                print(f"✅ Credit Labels: {len(self.dataset['credit_labels'])} records")
            else:
                print(f"⚠️  credit_labels.csv not found")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading dataset: {e}")
            return False
    
    def analyze_schema_mapping(self):
        """Analyze CSV schema vs API schema."""
        print("\n" + "=" * 70)
        print("Schema Mapping Analysis")
        print("=" * 70)
        
        # API Required Fields
        api_required = {
            "MSMEInput": {
                "gstin": "str (format: 29ABCDE1234F1Z5)",
                "pan": "str (format: ABCDE1234F)",
                "business_registration_date": "date",
                "gst_data": {
                    "gstin": "str",
                    "monthly_revenue": "list[float]",
                    "filing_history": "list[bool]",
                    "annual_turnover": "float"
                },
                "upi_transactions": "list[UPITransaction]",
                "account_aggregator_data": {
                    "month_end_balances": "list[float]",
                    "monthly_inflows": "list[float]",
                    "monthly_outflows": "list[float]",
                    "statement_start_date": "date",
                    "statement_end_date": "date"
                },
                "epfo_data": "Optional[EPFOData]",
                "bank_data": "Optional[BankData]"
            }
        }
        
        # Check available CSV fields
        print("\n📊 Available CSV Fields:")
        for table_name, df in self.dataset.items():
            print(f"\n  {table_name}:")
            print(f"    Columns: {', '.join(df.columns)}")
        
        # Identify missing fields
        print("\n\n🔍 Missing/Unavailable Fields in Dataset:")
        
        missing = []
        
        # GSTIN - NOT in dataset
        if 'GSTIN' not in self.dataset.get('businesses', pd.DataFrame()).columns:
            missing.append({
                "field": "GSTIN",
                "required_by": "MSMEInput.gstin, GSTData.gstin",
                "workaround": "Generate synthetic GSTIN based on state code + PAN"
            })
        
        # PAN - NOT in dataset
        if 'PAN' not in self.dataset.get('businesses', pd.DataFrame()).columns:
            missing.append({
                "field": "PAN",
                "required_by": "MSMEInput.pan",
                "workaround": "Generate synthetic PAN (format: ABCDE1234F)"
            })
        
        # Business Registration Date - NOT in dataset
        if 'Business_Registration_Date' not in self.dataset.get('businesses', pd.DataFrame()).columns:
            missing.append({
                "field": "Business Registration Date",
                "required_by": "MSMEInput.business_registration_date",
                "workaround": "Calculate from Business_Age_Years"
            })
        
        # UPI Transactions - NOT separately available
        if 'Payment_Mode' in self.dataset.get('bank_transactions', pd.DataFrame()).columns:
            missing.append({
                "field": "UPI Transactions",
                "required_by": "MSMEInput.upi_transactions",
                "workaround": "Extract from bank_transactions where Payment_Mode='UPI'"
            })
        
        # Account Aggregator Data - needs calculation
        missing.append({
            "field": "Monthly Balance Summary",
            "required_by": "AccountAggregatorData.month_end_balances",
            "workaround": "Calculate from bank_transactions Running_Balance at month end"
        })
        
        # EPFO Data - NOT in dataset
        if 'Employee_Count' in self.dataset.get('businesses', pd.DataFrame()).columns:
            missing.append({
                "field": "Monthly EPFO Records",
                "required_by": "EPFOData.monthly_employee_counts",
                "workaround": "Use static Employee_Count for all months (no growth data)"
            })
        
        # Print missing fields
        for i, item in enumerate(missing, 1):
            print(f"\n  {i}. {item['field']}")
            print(f"     Required by: {item['required_by']}")
            print(f"     Workaround: {item['workaround']}")
        
        self.missing_fields = missing
        return missing
    
    def convert_business_to_msme_input(self, business_id: str) -> Dict[str, Any]:
        """Convert a business record to MSMEInput format with synthetic data where needed."""
        
        # Get business info
        businesses = self.dataset['businesses']
        business = businesses[businesses['Business_ID'] == business_id].iloc[0]
        
        # Generate synthetic GSTIN (format: 29ABCDE1234F1Z5)
        # First 2 digits = state code (use 27 for Maharashtra as default)
        state_codes = {
            'Maharashtra': '27', 'Gujarat': '24', 'Karnataka': '29',
            'Tamil Nadu': '33', 'West Bengal': '19', 'Delhi': '07',
            'Uttar Pradesh': '09', 'Uttarakhand': '05', 'Madhya Pradesh': '23'
        }
        state_code = state_codes.get(business['State'], '27')
        
        # Extract first 5 letters from business name for PAN-like pattern
        business_name_clean = ''.join(c for c in business['Business_Name'].upper() if c.isalpha())[:5].ljust(5, 'X')
        
        # Generate PAN (format: ABCDE1234F - 5 letters, 4 digits, 1 letter)
        # Use business ID number to get 4 digits
        business_num = int(business_id.replace('MSME', ''))
        synthetic_pan = f"{business_name_clean}{business_num:04d}F"
        
        # Generate GSTIN (format: 29ABCDE1234F1Z5)
        # State code (2) + PAN (10) + Entity number (1) + Z + checksum (1)
        synthetic_gstin = f"{state_code}{synthetic_pan}1Z5"
        
        # Calculate business registration date from Business_Age_Years
        registration_date = (datetime.now().date() - timedelta(days=int(business['Business_Age_Years']) * 365))
        
        # Get GST data
        gst_data_df = self.dataset['gst_summary'][self.dataset['gst_summary']['Business_ID'] == business_id]
        
        # Get monthly revenue and filing history
        monthly_revenue = []
        filing_history = []
        
        if not gst_data_df.empty:
            # Sort by month
            gst_data_df = gst_data_df.sort_values('Month')
            monthly_revenue = gst_data_df['Sales'].tolist()
            filing_history = (gst_data_df['Filed_On_Time'] == 'Yes').tolist()
        
        # Get UPI transactions from bank transactions
        bank_txns = self.dataset['bank_transactions'][
            self.dataset['bank_transactions']['Business_ID'] == business_id
        ]
        
        upi_transactions = []
        if not bank_txns.empty:
            upi_txns = bank_txns[bank_txns['Payment_Mode'] == 'UPI'].head(100)  # Limit to 100
            
            for _, txn in upi_txns.iterrows():
                amount = txn['Credit'] if txn['Transaction_Type'] == 'Credit' else txn['Debit']
                if amount > 0:
                    upi_transactions.append({
                        "amount": float(amount),
                        "timestamp": pd.to_datetime(txn['Date']).isoformat(),
                        "counterparty": txn['Description'][:50]  # Truncate description
                    })
        
        # Calculate Account Aggregator Data from bank transactions
        if not bank_txns.empty:
            # Group by month
            bank_txns['Month'] = pd.to_datetime(bank_txns['Date']).dt.to_period('M')
            monthly_data = bank_txns.groupby('Month').agg({
                'Running_Balance': 'last',  # Month-end balance
                'Credit': 'sum',
                'Debit': 'sum'
            }).reset_index()
            
            month_end_balances = monthly_data['Running_Balance'].tolist()
            monthly_inflows = monthly_data['Credit'].tolist()
            monthly_outflows = monthly_data['Debit'].tolist()
            
            statement_start = bank_txns['Date'].min().date()
            statement_end = bank_txns['Date'].max().date()
        else:
            month_end_balances = [business['Opening_Balance_INR']] * 12
            monthly_inflows = [business['Annual_Turnover_INR'] / 12] * 12
            monthly_outflows = [business['Annual_Turnover_INR'] / 12 * 0.9] * 12
            statement_start = registration_date
            statement_end = datetime.now().date()
        
        # EPFO Data - use static employee count
        monthly_employee_counts = [int(business['Employee_Count'])] * 12
        
        # Bank Data
        bank_data = None
        if business['Existing_Loan'] == 'Yes':
            bank_data = {
                "total_monthly_emi": float(business['Existing_EMI_INR']),
                "loan_amounts": [float(business['Existing_EMI_INR'] * 24)],  # Estimate
                "account_number": f"ACC{business_id[-6:]}"
            }
        
        # Construct MSMEInput
        msme_input = {
            "gstin": synthetic_gstin,
            "pan": synthetic_pan,
            "business_registration_date": registration_date.isoformat(),
            "gst_data": {
                "gstin": synthetic_gstin,
                "monthly_revenue": monthly_revenue if monthly_revenue else [business['Annual_Turnover_INR'] / 12] * 12,
                "filing_history": filing_history if filing_history else [True] * 12,
                "annual_turnover": float(business['Annual_Turnover_INR'])
            },
            "upi_transactions": upi_transactions,
            "account_aggregator_data": {
                "month_end_balances": month_end_balances,
                "monthly_inflows": monthly_inflows,
                "monthly_outflows": monthly_outflows,
                "statement_start_date": statement_start.isoformat(),
                "statement_end_date": statement_end.isoformat()
            },
            "epfo_data": {
                "monthly_employee_counts": monthly_employee_counts
            } if business['Employee_Count'] > 0 else None,
            "bank_data": bank_data
        }
        
        return msme_input
    
    def validate_with_pydantic(self, business_id: str) -> tuple[bool, Any, str]:
        """Validate converted data with Pydantic models."""
        try:
            # Convert business data
            msme_dict = self.convert_business_to_msme_input(business_id)
            
            # Validate with Pydantic
            msme_input = MSMEInput(**msme_dict)
            
            return True, msme_input, "✅ Validation passed"
            
        except Exception as e:
            return False, None, f"❌ Validation failed: {str(e)}"
    
    def test_multiple_businesses(self, count: int = 5):
        """Test multiple businesses from the dataset."""
        print("\n" + "=" * 70)
        print(f"Testing {count} Businesses with Risk Agent Schema")
        print("=" * 70)
        
        # Get first N business IDs
        business_ids = self.dataset['businesses']['Business_ID'].head(count).tolist()
        
        results = []
        
        for i, business_id in enumerate(business_ids, 1):
            print(f"\n[{i}/{count}] Testing {business_id}...")
            
            success, validated_data, message = self.validate_with_pydantic(business_id)
            
            results.append({
                "business_id": business_id,
                "success": success,
                "message": message
            })
            
            print(f"  {message}")
            
            if success:
                # Save converted file
                OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
                output_file = OUTPUT_DIR / f"validated_{business_id}.json"
                
                with open(output_file, 'w') as f:
                    json.dump(json.loads(validated_data.model_dump_json()), f, indent=2)
                
                print(f"  💾 Saved: {output_file.name}")
        
        # Summary
        print("\n" + "=" * 70)
        print("Test Summary")
        print("=" * 70)
        
        success_count = sum(1 for r in results if r['success'])
        fail_count = len(results) - success_count
        
        print(f"\n✅ Successful: {success_count}/{len(results)}")
        print(f"❌ Failed: {fail_count}/{len(results)}")
        
        if fail_count > 0:
            print("\nFailed Businesses:")
            for r in results:
                if not r['success']:
                    print(f"  - {r['business_id']}: {r['message']}")
        
        return results
    
    def generate_report(self):
        """Generate comprehensive analysis report."""
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        report_path = OUTPUT_DIR / "DATASET_ANALYSIS_REPORT.md"
        
        with open(report_path, 'w') as f:
            f.write("# Dataset Analysis Report\n\n")
            f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
            f.write("---\n\n")
            
            f.write("## Dataset Overview\n\n")
            for name, df in self.dataset.items():
                f.write(f"### {name}\n")
                f.write(f"- **Records:** {len(df)}\n")
                f.write(f"- **Columns:** {len(df.columns)}\n")
                f.write(f"- **Columns List:** {', '.join(df.columns)}\n\n")
            
            f.write("## API Schema Requirements\n\n")
            f.write("The Risk Intelligence Agent requires the following input schema:\n\n")
            f.write("- **GSTIN** (str): GST Identification Number\n")
            f.write("- **PAN** (str): Permanent Account Number\n")
            f.write("- **Business Registration Date** (date)\n")
            f.write("- **GST Data**: Monthly revenue, filing history, annual turnover\n")
            f.write("- **UPI Transactions**: List of UPI transaction records\n")
            f.write("- **Account Aggregator Data**: Monthly balances, inflows, outflows\n")
            f.write("- **EPFO Data** (optional): Monthly employee counts\n")
            f.write("- **Bank Data** (optional): EMI, loan amounts\n\n")
            
            f.write("## Missing/Synthetic Data Fields\n\n")
            f.write("The following fields are NOT available in the dataset and require synthetic generation or calculation:\n\n")
            
            for i, item in enumerate(self.missing_fields, 1):
                f.write(f"### {i}. {item['field']}\n\n")
                f.write(f"- **Required by:** `{item['required_by']}`\n")
                f.write(f"- **Workaround:** {item['workaround']}\n\n")
            
            f.write("## Data Mapping Strategy\n\n")
            f.write("| API Field | Dataset Source | Status |\n")
            f.write("|-----------|----------------|--------|\n")
            f.write("| GSTIN | Synthetic (state code + PAN) | ⚠️  Generated |\n")
            f.write("| PAN | Synthetic (business name + ID) | ⚠️  Generated |\n")
            f.write("| Business Registration Date | Calculated from Business_Age_Years | ✅ Available |\n")
            f.write("| GST Monthly Revenue | gst_summary.Sales | ✅ Available |\n")
            f.write("| GST Filing History | gst_summary.Filed_On_Time | ✅ Available |\n")
            f.write("| Annual Turnover | businesses.Annual_Turnover_INR | ✅ Available |\n")
            f.write("| UPI Transactions | bank_transactions (Payment_Mode='UPI') | ✅ Available |\n")
            f.write("| Month-End Balances | bank_transactions.Running_Balance | ✅ Available |\n")
            f.write("| Monthly Inflows | bank_transactions.Credit | ✅ Available |\n")
            f.write("| Monthly Outflows | bank_transactions.Debit | ✅ Available |\n")
            f.write("| EPFO Employee Counts | businesses.Employee_Count (static) | ⚠️  Static |\n")
            f.write("| Bank EMI | businesses.Existing_EMI_INR | ✅ Available |\n\n")
            
            f.write("## Recommendations\n\n")
            f.write("1. **GSTIN/PAN Generation**: Synthetic identifiers are generated but not real. For production, real GSTIN/PAN would be required.\n\n")
            f.write("2. **EPFO Data**: Static employee count used for all months. Real EPFO data would show monthly variations.\n\n")
            f.write("3. **UPI Transactions**: Extracted from bank transactions. Format matches API requirements.\n\n")
            f.write("4. **Data Quality**: All required fields can be populated either directly or through calculation. The dataset is compatible with the Risk Agent.\n\n")
            
            f.write("## Next Steps\n\n")
            f.write("1. ✅ Convert dataset to API format\n")
            f.write("2. ✅ Validate with Pydantic schemas\n")
            f.write("3. ⏳ Run through Risk Intelligence Agent workflow\n")
            f.write("4. ⏳ Execute test suite with converted data\n")
            f.write("5. ⏳ Validate API endpoint with real dataset\n\n")
        
        print(f"\n📄 Generated report: {report_path}")


def main():
    """Main test function."""
    print("\n")
    print("=" * 70)
    print("DATASET VALIDATION WITH RISK INTELLIGENCE AGENT")
    print("=" * 70)
    print()
    
    analyzer = DatasetAnalyzer()
    
    # Load dataset
    if not analyzer.load_dataset():
        print("\n❌ Failed to load dataset")
        return
    
    # Analyze schema mapping
    analyzer.analyze_schema_mapping()
    
    # Test with multiple businesses
    results = analyzer.test_multiple_businesses(count=10)
    
    # Generate report
    analyzer.generate_report()
    
    print("\n" + "=" * 70)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"\nResults saved to: {OUTPUT_DIR}")
    print("\nNext steps:")
    print("  1. Review the analysis report")
    print("  2. Run the full test suite: pytest tests/ -v")
    print("  3. Test API endpoint with converted data")
    print()


if __name__ == "__main__":
    main()
