# Mock Underwriting Gateway & Onboarding State Machine

This directory contains the mock architecture specifications, JSON data contracts, and frontend state machine definitions for the MSME credit underwriting demo targeting New-to-Credit (NTC) borrowers.

---

## 1. Directory Inventory

- **[state_machine.ts](file:///a:/GitHub/MSME360/mock_gateway/state_machine.ts)**: TypeScript specification of the 3-step onboarding journey state machine. Defines the context schema, validation states (`IDLE`, `COLLECTING_BUSINESS_DETAILS`, `UPLOADING_KYC`, `VERIFYING_KYC`, `CONNECTING_DIGITAL_DATA`, `POLLING_APIS`, `FALLBACK_UPLOADS`, `ANALYZING`, `SUCCESS`, `FAILED`), and event-driven transition logic.
- **[mock_server.py](file:///a:/GitHub/MSME360/mock_gateway/mock_server.py)**: A Python FastAPI application providing hardcoded JSON payloads representing a successful underwriting scenario for a Kirana store.
- **[test_endpoints.py](file:///a:/GitHub/MSME360/mock_gateway/test_endpoints.py)**: Automated end-to-end integration test runner validating all mock endpoints.
- **[requirements.txt](file:///a:/GitHub/MSME360/mock_gateway/requirements.txt)**: Core dependencies.
- **[run_mock.ps1](file:///a:/GitHub/MSME360/mock_gateway/run_mock.ps1)**: Windows PowerShell runner to start the server.

---

## 2. Onboarding User Journey States

The state machine in `state_machine.ts` coordinates the following steps:

```
[IDLE]
  │
  ▼ (START)
[Step 1: COLLECTING_BUSINESS_DETAILS] (Business Details Form)
  │
  ▼ (SUBMIT_BUSINESS_DETAILS)
[Step 2: UPLOADING_KYC] (Aadhaar, PAN & Udyam Upload Panels)
  │
  ▼ (SUBMIT_KYC_DOCUMENTS)
[VERIFYING_KYC] (Simulating background validation)
  │
  ├─► KYC_VERIFICATION_SUCCESS ──► [Step 3: CONNECTING_DIGITAL_DATA] (Connect GST/AA/UPI/EPFO Buttons)
  └─► KYC_VERIFICATION_FAILURE ──► [FAILED]
```

### Digital Connection & Fallback Workflow:
1. In **`CONNECTING_DIGITAL_DATA`**, the user clicks "Connect" buttons for GST, AA, UPI, and EPFO.
2. If the user clicks connect and the API succeeds, the system transitions to **`POLLING_APIS`**. Once the user clicks "Analyze", the system transitions to **`ANALYZING`**.
3. **API Failures / Fallback**: If digital connection APIs fail (e.g. consent timeout or network issues), the UI transitions immediately to **`FALLBACK_UPLOADS`**, requesting physical uploads:
   - Bank Statement (Last 6-12 Months PDF)
   - GST Registration Certificate (PDF)
   Submitting fallback uploads transitions the UI to **`ANALYZING`**.

---

## 3. Mock Endpoint API Contracts

All endpoints return unified JSON structures representing a successful underwriting scenario:

### 1. `POST /api/v1/kyc/verify` (NSDL / UIDAI / Udyam validation)
Expects form-data fields: `pan_number`, `aadhaar_number`, `udyam_number` (plus optional PDF files).
Returns:
```json
{
  "status": "VERIFIED",
  "kyc_data": {
    "pan": {
      "status": "VALID",
      "pan_number": "ABCDE1234F",
      "name_on_card": "GUWAHATI KIRANA & GENERAL STORE (Prop: Ayesha Mehta)",
      "match_score": 0.98,
      "category": "Proprietorship"
    },
    "aadhaar": {
      "status": "VALID",
      "uidai_linked_phone": "XXXXXX9876",
      "demographic_match": true,
      "dob_verified": true
    },
    "udyam": {
      "status": "VALID",
      "registration_number": "UDYAM-AS-01-0012345",
      "enterprise_name": "GUWAHATI KIRANA STORE",
      "enterprise_type": "Micro",
      "major_activity": "Services (Retail Trade)",
      "incorporation_date": "2018-04-12"
    }
  },
  "verification_timestamp": "2026-07-07T17:35:00.000000Z"
}
```

### 2. `POST /api/v1/financial/connect` (Simulates alternate-data connections)
Expects JSON payload with connection toggles. Can be triggered with query parameter `?simulate_failure=true` to simulate connection failures and test the fallback UI.
Returns:
```json
{
  "status": "CONNECTED",
  "sources": {
    "gst": {
      "connected": true,
      "average_monthly_sales_inr": 625000.00,
      "filing_regularity": "12/12 Months (100% on time)",
      "last_filed_month": "2026-05",
      "gstin": "18AAAAA0000A1Z9"
    },
    "account_aggregator": {
      "connected": true,
      "average_balance_inr": 125000.00,
      "expense_to_income_ratio": 0.82,
      "cash_buffer_days": 18,
      "bounce_events_12m": 0
    },
    "upi": {
      "connected": true,
      "monthly_transaction_volume_inr": 280000.00,
      "unique_customers_per_month": 450,
      "digital_penetration_rate": 0.85,
      "payment_gateway": "BharatPe QR"
    },
    "epfo": {
      "connected": true,
      "active_employee_count": 6,
      "monthly_payroll_inr": 72000.00,
      "deposit_regularity": "Consistent (Last 6 Months)"
    }
  },
  "timestamp": "2026-07-07T17:35:01.000000Z"
}
```

### 3. `POST /api/v1/credit-copilot/evaluate` (Consumes outputs of financial & compliance agents)
Returns complete financial evaluations:
```json
{
  "status": "APPROVED",
  "financial_health_card": {
    "health_score": 82,
    "grade": "A-",
    "metrics": [
      {"label": "Alternate-Data Turnover (GST)", "value": "₹75 Lakhs (Annualized)", "status": "success"},
      {"label": "Expense Ratio", "value": "82%", "status": "success"},
      {"label": "Cash Buffer Days", "value": "18 Days", "status": "success"},
      {"label": "Payment Bounces (12m)", "value": "0 Bounces", "status": "success"},
      {"label": "Filing Regularity (GSTR-3B)", "value": "100% On-Time", "status": "success"}
    ]
  },
  "loan_recommendation": {
    "approved_amount_inr": 2500000.00,
    "interest_rate_pct": 11.5,
    "tenure_months": 24,
    "monthly_emi_inr": 117094.00,
    "product_type": "Working Capital Loan"
  },
  "risk_explanation": [
    "Positive: Digital payment penetration of 85% matches growing kirana trends.",
    "Risk Factor: Absence of traditional credit registry file (New-To-Credit borrower)."
  ],
  "credit_memo_markdown": "... (Complete underwriter memo text) ...",
  "evaluation_timestamp": "2026-07-07T17:35:02.000000Z"
}
```

---

## 4. Running the Servers and Tests

### Installation
Ensure you have the required dependencies:
```powershell
pip install -r mock_gateway/requirements.txt
```

### Run Server
Start the mock API gateway:
```powershell
cd mock_gateway
python mock_server.py
```
*(Or execute `.\mock_gateway\run_mock.ps1` from the project root).*

### Run Tests
To run the automated verification checks:
```powershell
python mock_gateway/test_endpoints.py
```
