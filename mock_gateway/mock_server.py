from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import datetime

app = FastAPI(
    title="MSME Alternate-Data Credit Underwriting Mock API",
    description="Mock gateway endpoints for KYC verification, Digital Connections, and Credit Copilot evaluations (Track 3 prototype).",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Input Models ---
class KYCVerificationRequest(BaseModel):
    pan_number: str
    aadhaar_number: str
    udyam_number: str


class ConnectAPIRequest(BaseModel):
    connect_gst: bool = True
    connect_aa: bool = True
    connect_upi: bool = True
    connect_epfo: bool = True


# --- Endpoints ---

@app.get("/")
def root():
    return {
        "service": "MSME Alternate-Data Mock Gateway",
        "endpoints": {
            "kyc_verification": "POST /api/v1/kyc/verify",
            "digital_connections": "POST /api/v1/financial/connect",
            "credit_evaluation": "POST /api/v1/credit-copilot/evaluate"
        },
        "status": "ready"
    }


@app.post("/api/v1/kyc/verify")
async def verify_kyc(
    pan_number: str = Form(..., description="Business or individual PAN"),
    aadhaar_number: str = Form(..., description="12-digit Aadhaar number"),
    udyam_number: str = Form(..., description="Udyam Certificate Registration ID"),
    pan_file: Optional[UploadFile] = File(None, description="PAN Card PDF/Image upload")
):
    """
    KYC Verification Mock.
    Simulates validation checks against NSDL (PAN), UIDAI (Aadhaar), and Udyam Portal.
    """
    clean_pan = pan_number.upper().strip()
    
    # Simple validation formatting checks
    if len(clean_pan) != 10:
        raise HTTPException(status_code=400, detail="Invalid PAN Card format. Must be 10 characters.")
    if len(aadhaar_number.strip()) != 12 or not aadhaar_number.strip().isdigit():
        raise HTTPException(status_code=400, detail="Invalid Aadhaar format. Must be a 12-digit number.")
        
    return {
        "status": "VERIFIED",
        "kyc_data": {
            "pan": {
                "status": "VALID",
                "pan_number": clean_pan,
                "name_on_card": "GUWAHATI KIRANA & GENERAL STORE (Prop: Ayesha Mehta)",
                "match_score": 0.98,
                "category": "Proprietorship"
            },
            "aadhaar": {
                "status": "VALID",
                "uidai_linked_phone": "XXXXXX9876",
                "demographic_match": True,
                "dob_verified": True
            },
            "udyam": {
                "status": "VALID",
                "registration_number": udyam_number.upper().strip(),
                "enterprise_name": "GUWAHATI KIRANA STORE",
                "enterprise_type": "Micro",
                "major_activity": "Services (Retail Trade)",
                "incorporation_date": "2018-04-12"
            }
        },
        "verification_timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }


@app.post("/api/v1/financial/connect")
def connect_financials(
    request: ConnectAPIRequest,
    simulate_failure: bool = Query(
        False, 
        description="Toggle to simulate connection failure (e.g. AA or GST consent times out)"
    )
):
    """
    Digital Data Connector Mock.
    Simulates consent-based feeds from GST, Account Aggregator, UPI, and EPFO.
    If `simulate_failure` is true, returns API failure response to test the Fallback Flow.
    """
    if simulate_failure:
        return {
            "status": "FAILED",
            "error_code": "CONSENT_TIMEOUT",
            "error_message": "Consent authorization timed out from the Account Aggregator portal (AA-9284). Redirecting to document fallback flow.",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        }

    return {
        "status": "CONNECTED",
        "sources": {
            "gst": {
                "connected": request.connect_gst,
                "average_monthly_sales_inr": 625000.00,
                "filing_regularity": "12/12 Months (100% on time)",
                "last_filed_month": "2026-05",
                "gstin": "18AAAAA0000A1Z9"
            },
            "account_aggregator": {
                "connected": request.connect_aa,
                "average_balance_inr": 125000.00,
                "expense_to_income_ratio": 0.82,
                "cash_buffer_days": 18,
                "bounce_events_12m": 0
            },
            "upi": {
                "connected": request.connect_upi,
                "monthly_transaction_volume_inr": 280000.00,
                "unique_customers_per_month": 450,
                "digital_penetration_rate": 0.85,
                "payment_gateway": "BharatPe QR"
            },
            "epfo": {
                "connected": request.connect_epfo,
                "active_employee_count": 6,
                "monthly_payroll_inr": 72000.00,
                "deposit_regularity": "Consistent (Last 6 Months)"
            }
        },
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }


@app.post("/api/v1/credit-copilot/evaluate")
def evaluate_credit(payload: Dict):
    """
    Credit Copilot Orchestrator Evaluation Mock.
    Consumes verified KYC and Financial connector schemas.
    Generates Health Card metrics, loan recommendation details, and credit memo markdown.
    """
    credit_memo = (
        "# CREDIT MEMO: GUWAHATI KIRANA STORE\n"
        "**Date**: July 07, 2026 | **Underwriter ID**: CreditPulse-AI\n\n"
        "## Executive Summary\n"
        "Guwahati Kirana Store is a sole proprietorship operating in the retail grocery sector since 2018. "
        "The applicant seeks a working capital exposure of ₹2.5 Cr. The applicant lacks standard audited balance sheets "
        "but exhibits exceptionally healthy alternative digital indicators.\n\n"
        "## Underwriting Rationale\n"
        "1. **Alternate-Revenue Stability**: Monthly turnover averages ₹6.25L, backed by strong, consistent GSTR-1 records. "
        "All 12 returns were filed on time.\n"
        "2. **Strong Digital Realization**: Over 85% of customer transactions occur digitally via UPI (average 450 unique customers/mo), "
        "demonstrating low customer concentration and solid business popularity.\n"
        "3. **Sufficient Cash Buffers**: The bank statement linked via Account Aggregator demonstrates an average balance "
        "of ₹1.25L (approx. 18 days of operating expenses) with zero cheque bounces or payment defaults recorded over 12 months.\n"
        "4. **KYC & Compliance Verification**: PAN registration matches Ayesha Mehta. Aadhaar biometric link confirmed. "
        "Udyam registration establishes the Micro Enterprise classification, satisfying the priority sector landing guidelines.\n\n"
        "## Recommendation\n"
        "We recommend **Approve Working Capital Loan** at a competitive interest band of 11.5% with a 24-month tenure."
    )

    return {
        "status": "APPROVED",
        "financial_health_card": {
            "health_score": 82,
            "grade": "A-",
            "metrics": [
                {"label": "Alternate-Data Turnover (GST)", "value": "\u20b975 Lakhs (Annualized)", "status": "success"},
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
            "Positive: Digital payment penetration of 85% matches growing retail kirana trends.",
            "Positive: Micro Enterprise status verified with complete tax transparency.",
            "Positive: Consistent EPFO records indicate operational stability and employee retention.",
            "Risk Factor: Absence of traditional credit registry file (New-To-Credit borrower).",
            "Risk Factor: Volatility in monthly cash flows corresponding to agricultural harvest seasons."
        ],
        "credit_memo_markdown": credit_memo,
        "evaluation_timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }
