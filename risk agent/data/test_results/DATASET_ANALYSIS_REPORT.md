# Dataset Analysis Report

**Generated:** 2026-07-07T16:34:20.813746

---

## Dataset Overview

### businesses
- **Records:** 425
- **Columns:** 20
- **Columns List:** Business_ID, Business_Name, Owner_Name, Industry, City, State, Business_Age_Years, Owner_Age, Employee_Count, Monthly_Operating_Days, Average_Daily_Customers, Annual_Turnover_INR, GST_Registered, Existing_Loan, Existing_EMI_INR, Working_Capital_INR, Credit_Limit_INR, Business_Category, Personality_Tag, Opening_Balance_INR

### gst_summary
- **Records:** 5052
- **Columns:** 12
- **Columns List:** Business_ID, Month, Sales, Taxable_Sales, GST_Paid, GST_Liability, Return_Filing_Date, Filed_On_Time, Late_Days, Input_Tax_Credit, Output_Tax, Refund

### bank_transactions
- **Records:** 809958
- **Columns:** 10
- **Columns List:** Transaction_ID, Business_ID, Date, Description, Transaction_Type, Payment_Mode, Category, Credit, Debit, Running_Balance

### engineered_features
- **Records:** 425
- **Columns:** 23
- **Columns List:** Business_ID, Business_Name, Industry, Average_Monthly_Revenue, Average_Monthly_Expense, Expense_Ratio, Cash_Buffer_Days, Average_Balance, Minimum_Balance, Maximum_Balance, Income_Volatility, Revenue_Growth, GST_Regularity_Score, Bounce_Count, Monthly_Savings_Rate, EMI_Ratio, Credit_Frequency, Debit_Frequency, Cash_Deposit_Ratio, Digital_Payment_Ratio, Business_Stability_Index, Growth_Index, Liquidity_Score

### credit_labels
- **Records:** 425
- **Columns:** 10
- **Columns List:** Business_ID, Business_Name, Financial_Health_Score, Risk_Category, Confidence, Recommended_Loan_Amount, Recommended_Tenure_Months, Recommended_Interest_Band, Approval_Decision, Scoring_Rationale

## API Schema Requirements

The Risk Intelligence Agent requires the following input schema:

- **GSTIN** (str): GST Identification Number
- **PAN** (str): Permanent Account Number
- **Business Registration Date** (date)
- **GST Data**: Monthly revenue, filing history, annual turnover
- **UPI Transactions**: List of UPI transaction records
- **Account Aggregator Data**: Monthly balances, inflows, outflows
- **EPFO Data** (optional): Monthly employee counts
- **Bank Data** (optional): EMI, loan amounts

## Missing/Synthetic Data Fields

The following fields are NOT available in the dataset and require synthetic generation or calculation:

### 1. GSTIN

- **Required by:** `MSMEInput.gstin, GSTData.gstin`
- **Workaround:** Generate synthetic GSTIN based on state code + PAN

### 2. PAN

- **Required by:** `MSMEInput.pan`
- **Workaround:** Generate synthetic PAN (format: ABCDE1234F)

### 3. Business Registration Date

- **Required by:** `MSMEInput.business_registration_date`
- **Workaround:** Calculate from Business_Age_Years

### 4. UPI Transactions

- **Required by:** `MSMEInput.upi_transactions`
- **Workaround:** Extract from bank_transactions where Payment_Mode='UPI'

### 5. Monthly Balance Summary

- **Required by:** `AccountAggregatorData.month_end_balances`
- **Workaround:** Calculate from bank_transactions Running_Balance at month end

### 6. Monthly EPFO Records

- **Required by:** `EPFOData.monthly_employee_counts`
- **Workaround:** Use static Employee_Count for all months (no growth data)

## Data Mapping Strategy

| API Field | Dataset Source | Status |
|-----------|----------------|--------|
| GSTIN | Synthetic (state code + PAN) | ⚠️  Generated |
| PAN | Synthetic (business name + ID) | ⚠️  Generated |
| Business Registration Date | Calculated from Business_Age_Years | ✅ Available |
| GST Monthly Revenue | gst_summary.Sales | ✅ Available |
| GST Filing History | gst_summary.Filed_On_Time | ✅ Available |
| Annual Turnover | businesses.Annual_Turnover_INR | ✅ Available |
| UPI Transactions | bank_transactions (Payment_Mode='UPI') | ✅ Available |
| Month-End Balances | bank_transactions.Running_Balance | ✅ Available |
| Monthly Inflows | bank_transactions.Credit | ✅ Available |
| Monthly Outflows | bank_transactions.Debit | ✅ Available |
| EPFO Employee Counts | businesses.Employee_Count (static) | ⚠️  Static |
| Bank EMI | businesses.Existing_EMI_INR | ✅ Available |

## Recommendations

1. **GSTIN/PAN Generation**: Synthetic identifiers are generated but not real. For production, real GSTIN/PAN would be required.

2. **EPFO Data**: Static employee count used for all months. Real EPFO data would show monthly variations.

3. **UPI Transactions**: Extracted from bank transactions. Format matches API requirements.

4. **Data Quality**: All required fields can be populated either directly or through calculation. The dataset is compatible with the Risk Agent.

## Next Steps

1. ✅ Convert dataset to API format
2. ✅ Validate with Pydantic schemas
3. ⏳ Run through Risk Intelligence Agent workflow
4. ⏳ Execute test suite with converted data
5. ⏳ Validate API endpoint with real dataset

