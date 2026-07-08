from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import logging
import pandas as pd
import os
import sys
import json
from pydantic import BaseModel
from datetime import datetime, timezone, date, timedelta
import random
import re
from typing import Optional, List

logger = logging.getLogger("msme360")
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass

# Add risk agent to path to allow importing its modules
RISK_AGENT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "risk agent")
if RISK_AGENT_DIR not in sys.path:
    sys.path.insert(0, RISK_AGENT_DIR)

from db import (
    init_db, get_db_connection, add_audit_event, get_audit_events,
    add_custom_business, get_custom_businesses, get_custom_business_detail
)
from agent1_intake import check_compliance_rules
from agent3_copilot import call_llm
from agents.risk_intelligence_agent.workflow import evaluate_msme
from agents.risk_intelligence_agent.schemas import MSMEInput, GSTData, AccountAggregatorData, UPITransaction, EPFOData, BankData
from creditpilot_orchestrator import get_orchestrator
from creditpilot_conversation import get_conversation_handler, ConversationRequest
from auth import (
    LoginRequest, LoginResponse, UserInfo,
    authenticate, create_access_token, get_current_user,
    init_auth_tables, require_customer, require_officer,
)

app = FastAPI(title="MSME Credit Workspace Backend")

# CORS driven by env var; falls back to a strict localhost allowlist so
# credentials-cookie/token flows can't be exercised from arbitrary origins.
_default_origins = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174"
_allowed_origins = [
    o.strip() for o in os.environ.get("CORS_ALLOW_ORIGINS", _default_origins).split(",") if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Initialize database on startup
init_db()
init_auth_tables()

@app.get("/api/health")
def health():
    return {"status": "healthy"}


# ============================================================================
# AUTH ENDPOINTS
# ============================================================================

@app.post("/api/auth/login", response_model=LoginResponse)
def login(req: LoginRequest):
    user = authenticate(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token, expires = create_access_token(user.username, user.role)
    return LoginResponse(
        access_token=token,
        role=user.role,
        username=user.username,
        expires_at=expires.isoformat(),
    )


@app.get("/api/auth/me", response_model=UserInfo)
def me(user: UserInfo = Depends(get_current_user)):
    return user


# ============================================================================
# OCR / DOCUMENT INTELLIGENCE ENDPOINT
# ============================================================================

GEMINI_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

def _extract_via_gemini_vision(image_bytes: bytes, mime_type: str) -> dict:
    """Use Gemini Vision API to extract bank statement data from an image."""
    import base64
    import urllib.request
    import urllib.error

    b64_data = base64.b64encode(image_bytes).decode("utf-8")

    prompt = """You are analyzing a scanned Indian bank statement image. Extract the following fields as a JSON object. 
If a field is not visible, return null for it. Be precise with numbers.

Required JSON schema:
{
  "business_name": "Name of the business or account holder",
  "owner_name": "Name of the account holder / proprietor",
  "account_number": "Bank account number if visible",
  "ifsc_code": "IFSC code if visible",
  "bank_name": "Name of the bank",
  "pan_number": "PAN number if visible (format: ABCDE1234F)",
  "gstin": "GSTIN if visible",
  "statement_period_start": "Start date of statement (YYYY-MM-DD)",
  "statement_period_end": "End date of statement (YYYY-MM-DD)",
  "total_credits": total credit amount as number,
  "total_debits": total debit amount as number,
  "closing_balance": closing balance as number,
  "average_balance": average balance as number (estimate if not shown),
  "transaction_count": number of transactions visible,
  "industry_hint": "Guess the industry from transaction descriptions (e.g., Kirana Store, Textile, Manufacturing)"
}

Return ONLY the JSON object, no markdown fences or explanations."""

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_KEY,
        "User-Agent": "MSME360-OCR/1.0"
    }
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": mime_type, "data": b64_data}}
            ]
        }]
    }

    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers=headers, method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        res = json.loads(response.read().decode("utf-8"))
        raw_text = res["candidates"][0]["content"]["parts"][0]["text"].strip()

        # Strip markdown code fences if Gemini wraps the output
        if raw_text.startswith("```"):
            raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
            raw_text = re.sub(r"\s*```$", "", raw_text)

        return json.loads(raw_text)


def _extract_from_csv(csv_bytes: bytes, filename: str) -> dict:
    """Parse a CSV bank statement and extract financial summary fields."""
    import io
    df = pd.read_csv(io.BytesIO(csv_bytes))
    df.columns = [c.strip() for c in df.columns]

    # Coerce numeric columns
    for col in ["Credit", "Debit", "Running_Balance"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    total_credits = float(df["Credit"].sum()) if "Credit" in df.columns else 0
    total_debits = float(df["Debit"].sum()) if "Debit" in df.columns else 0
    avg_bal = float(df["Running_Balance"].mean()) if "Running_Balance" in df.columns else 0
    closing_bal = float(df["Running_Balance"].iloc[-1]) if "Running_Balance" in df.columns and len(df) > 0 else 0
    tx_count = len(df)

    # Date range
    period_start = None
    period_end = None
    if "Date" in df.columns:
        try:
            df["Date"] = pd.to_datetime(df["Date"])
            period_start = df["Date"].min().strftime("%Y-%m-%d")
            period_end = df["Date"].max().strftime("%Y-%m-%d")
        except Exception:
            pass

    # Industry hint from transaction descriptions
    industry_hint = "Retail Merchant"
    if "Description" in df.columns:
        desc_text = " ".join(df["Description"].dropna().astype(str).tolist()).lower()
        if any(w in desc_text for w in ["kirana", "grocery", "fmcg", "parle", "unilever", "britannia"]):
            industry_hint = "Kirana Store"
        elif any(w in desc_text for w in ["textile", "fabric", "silk", "garment", "weav"]):
            industry_hint = "Textile Manufacturing"
        elif any(w in desc_text for w in ["distributor", "wholesale", "supply chain"]):
            industry_hint = "FMCG Distribution"
        elif any(w in desc_text for w in ["agri", "farm", "seed", "fertilizer", "crop"]):
            industry_hint = "Agri-Processing"
        elif any(w in desc_text for w in ["steel", "iron", "metal", "casting"]):
            industry_hint = "Metal & Engineering"

    # Owner name hint from filename
    owner_hint = None
    name_from_file = filename.replace(".csv", "").replace("_", " ").replace("-", " ").title()
    if len(name_from_file) > 3 and not name_from_file.lower().startswith("bank"):
        owner_hint = name_from_file

    return {
        "business_name": owner_hint,
        "owner_name": None,
        "account_number": None,
        "ifsc_code": None,
        "bank_name": None,
        "pan_number": None,
        "gstin": None,
        "statement_period_start": period_start,
        "statement_period_end": period_end,
        "total_credits": round(total_credits, 2),
        "total_debits": round(total_debits, 2),
        "closing_balance": round(closing_bal, 2),
        "average_balance": round(avg_bal, 2),
        "transaction_count": tx_count,
        "industry_hint": industry_hint
    }


def _mock_image_extraction(filename: str) -> dict:
    """Fallback mock extraction when no Gemini API key is available."""
    return {
        "business_name": "Surat Silk Weaves",
        "owner_name": "Abhishek Mohapatra",
        "account_number": "IDBI-302948571",
        "ifsc_code": "IBKL0000123",
        "bank_name": "IDBI Bank",
        "pan_number": "ABCDE5678X",
        "gstin": "27ABCDE5678X1Z1",
        "statement_period_start": "2025-01-01",
        "statement_period_end": "2025-06-30",
        "total_credits": 2845000.0,
        "total_debits": 2190000.0,
        "closing_balance": 87500.0,
        "average_balance": 72000.0,
        "transaction_count": 340,
        "industry_hint": "Manufacturing",
        "_mock": True,
        "_note": "Set GEMINI_API_KEY in backend/.env for real Gemini Vision extraction"
    }


@app.post("/api/ocr/extract")
async def ocr_extract(file: UploadFile = File(...)):
    """
    Document Intelligence Endpoint.
    
    Accepts:
    - Image files (PNG/JPEG/WEBP) -> Gemini Vision API extraction
    - CSV files -> Direct pandas parsing and financial summary extraction
    
    Returns extracted fields to pre-fill the registration form.
    """
    file_bytes = await file.read()
    filename = file.filename or "upload"
    content_type = file.content_type or ""

    is_csv = (
        filename.lower().endswith(".csv") or
        "csv" in content_type.lower() or
        "text/" in content_type.lower()
    )
    is_image = (
        filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")) or
        "image/" in content_type.lower()
    )

    if not is_csv and not is_image:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported file type: {content_type}. Upload a CSV bank statement or an image (PNG/JPEG) of a paper statement."
        )

    try:
        if is_csv:
            extracted = _extract_from_csv(file_bytes, filename)
            source = "csv_parser"
        elif GEMINI_KEY:
            # Determine mime type for Gemini
            mime = "image/png"
            if filename.lower().endswith((".jpg", ".jpeg")):
                mime = "image/jpeg"
            elif filename.lower().endswith(".webp"):
                mime = "image/webp"
            elif "image/" in content_type:
                mime = content_type

            extracted = _extract_via_gemini_vision(file_bytes, mime)
            source = "gemini_vision"
        else:
            # No API key — return mock data for demo
            extracted = _mock_image_extraction(filename)
            source = "mock_fallback"

        return {
            "success": True,
            "source": source,
            "extracted": extracted
        }

    except Exception as e:
        logger.exception("OCR extraction failed for %s", filename)
        # On any extraction failure, return mock data so the UI stays functional
        # but honestly flag the failure via success=False; the frontend uses this
        # to display a "manual entry required" hint instead of silently trusting
        # fabricated numbers.
        return {
            "success": False,
            "source": "mock_fallback",
            "_error": type(e).__name__,
            "extracted": _mock_image_extraction(filename),
            "_error": str(e)
        }

DATASET_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Dataset")

# Dataset CSVs are used for TRAINING/ANALYTICS only, not displayed in production UI
# They are loaded here for backwards compatibility with analytics endpoints
# Production portfolio endpoint uses only custom_businesses table
try:
    FEAT_DF = pd.read_csv(os.path.join(DATASET_DIR, "engineered_features.csv"))
    LBL_DF = pd.read_csv(os.path.join(DATASET_DIR, "credit_labels.csv"))
    print(f"[OK] Loaded training dataset: {len(FEAT_DF)} businesses (for analytics/training only)")
except FileNotFoundError:
    # Gracefully handle missing files - not critical for production
    print("[!] Training dataset files not found - production features still available")
    FEAT_DF = pd.DataFrame()
    LBL_DF = pd.DataFrame()

def get_dynamic_profile(business_id: str, name: str, annual_turnover: float, avg_revenue: float, score: int):
    import hashlib
    seed_hash = int(hashlib.md5(name.encode("utf-8")).hexdigest(), 16)
    
    loc_list = [
        ("Mumbai", "Maharashtra"),
        ("Kolkata", "West Bengal"),
        ("Surat", "Gujarat"),
        ("Chennai", "Tamil Nadu"),
        ("Guwahati", "Assam"),
        ("Bengaluru", "Karnataka"),
        ("Hyderabad", "Telangana"),
        ("Noida", "Uttar Pradesh")
    ]
    
    if len(business_id) >= 15 and not business_id.startswith("MSME_UP_"):
        prefix = business_id[:2]
        gstin_map = {
            "27": ("Mumbai", "Maharashtra"),
            "19": ("Kolkata", "West Bengal"),
            "24": ("Surat", "Gujarat"),
            "33": ("Chennai", "Tamil Nadu"),
            "29": ("Bengaluru", "Karnataka"),
            "36": ("Hyderabad", "Telangana"),
            "07": ("New Delhi", "Delhi"),
            "09": ("Noida", "Uttar Pradesh")
        }
        city, state = gstin_map.get(prefix, loc_list[seed_hash % len(loc_list)])
    else:
        city, state = loc_list[seed_hash % len(loc_list)]
        
    first_names = ["Rajesh", "Amit", "Sanjay", "Vikram", "Sunita", "Aarav", "Meera", "Arjun", "Priya", "Rahul"]
    surnames = ["Patel", "Sharma", "Banerjee", "Mehta", "Joshi", "Iyer", "Rao", "Gupta", "Das", "Reddy"]
    owner = f"{first_names[seed_hash % len(first_names)]} {surnames[(seed_hash // len(first_names)) % len(surnames)]}"
    
    business_age_years = 3 + (seed_hash % 8)
    employee_count = max(3, min(120, int(annual_turnover / 800000) + (seed_hash % 5)))
    
    if annual_turnover < 50000000:
        category = "Micro"
    elif annual_turnover < 750000000:
        category = "Small"
    else:
        category = "Medium"
        
    multiplier = 1.2 if score >= 80 else (1.0 if score >= 65 else (0.7 if score >= 50 else 0.3))
    raw_loan = avg_revenue * 3 * multiplier
    loan_amount = int(round(raw_loan / 50000) * 50000)
    loan_amount = max(100000, min(50000000, loan_amount))
    
    return {
        "city": city,
        "state": state,
        "owner": owner,
        "business_age_years": business_age_years,
        "employee_count": employee_count,
        "category": category,
        "loan_amount": loan_amount
    }

@app.get("/api/portfolio")
def portfolio(_: UserInfo = Depends(require_officer)):
    """
    Returns real-time portfolio of applications.
    ONLY returns user-uploaded applications from custom_businesses table.
    Static dataset (FEAT_DF/LBL_DF) is used for training only, not displayed here.
    """
    # Query decisions from local SQLite DB
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT business_id, status FROM officer_decisions")
    decisions = {r["business_id"]: r["status"] for r in cursor.fetchall()}
    conn.close()

    rows = []
    
    # ONLY return real user-uploaded applications from custom_businesses table
    custom_list = get_custom_businesses()
    for c in custom_list:
        bid = c["business_id"]
        status = decisions.get(bid, "Pending")
        
        # Extract details dynamically from saved JSON data
        avg_revenue = 500000.0
        annual_turnover = 6000000.0
        try:
            data = json.loads(c["data_json"])
            
            # Handle different data structures (intake vs full evaluation)
            if "report" in data:
                # Full evaluation from /api/intake/register
                report = data["report"]
                trends = report.get("trends", [])
                if trends:
                    avg_revenue = sum(t["revenue"] for t in trends) / len(trends)
                gst_analysis = report.get("gst_analysis", {})
                annual_turnover = gst_analysis.get("annual_turnover", avg_revenue * 12)
            else:
                # Simple intake from /api/intake or direct evaluation
                trends = data.get("trends", [])
                if trends:
                    avg_revenue = sum(t["revenue"] for t in trends) / len(trends)
                gst_analysis = data.get("gst_analysis", {})
                if gst_analysis:
                    annual_turnover = gst_analysis.get("annual_turnover", avg_revenue * 12)
        except (KeyError, ValueError, TypeError, json.JSONDecodeError) as e:
            # Corrupt or partial JSON: log with the business id so operators can
            # locate the bad row. We intentionally do NOT swallow arbitrary
            # exceptions here — programming errors should surface as 500s.
            logger.warning("portfolio: could not parse data_json for %s: %s", bid, e)
            
        profile = get_dynamic_profile(bid, c["name"], annual_turnover, avg_revenue, int(c["score"]))
        
        rows.append({
            "business_id": bid,
            "name": c["name"],
            "industry": c["industry"],
            "city": profile["city"],
            "state": profile["state"],
            "category": profile["category"],
            "gst_registered": True,
            "score": int(c["score"]),
            "band": c["band"],
            "confidence": 0.95,
            "avg_monthly_revenue": float(avg_revenue),
            "model_decision": "Approve" if c["score"] >= 75 else ("Conditional Approval" if c["score"] >= 55 else "Reject"),
            "officer_status": status,
            "applied_at": c["applied_at"][:10]
        })

    # Static dataset (FEAT_DF/LBL_DF) is NOT included here - used for training only
    # To re-enable mock data for testing, uncomment the section below:
    
    # for _, row in merged.iterrows():
    #     bid = row["Business_ID"]
    #     status = decisions.get(bid, "Pending")
    #     ... (rest of static data processing)
    
    return rows


@app.get("/api/portfolio/analytics")
def portfolio_analytics(_: UserInfo = Depends(require_officer)):
    """
    Returns the static training dataset for analytics and model training purposes.
    This data is NOT shown in the officer dashboard - it's for data science/analysis only.
    """
    if FEAT_DF.empty or LBL_DF.empty:
        return {
            "error": "Training dataset not available",
            "message": "CSV files not found in Dataset directory"
        }
    
    merged = FEAT_DF.merge(
        LBL_DF[["Business_ID", "Financial_Health_Score", "Risk_Category", "Confidence"]], 
        on="Business_ID"
    )
    
    rows = []
    for _, row in merged.iterrows():
        rows.append({
            "business_id": row["Business_ID"],
            "name": row["Business_Name"],
            "industry": row["Industry"],
            "score": int(row["Financial_Health_Score"]),
            "band": row["Risk_Category"],
            "confidence": float(row["Confidence"]),
            "avg_monthly_revenue": float(row["Average_Monthly_Revenue"]),
            "purpose": "TRAINING_DATA_ONLY"
        })
    
    return {
        "count": len(rows),
        "data": rows,
        "note": "This is static training data, not real applications"
    }

@app.post("/api/intake")
async def upload_intake(bank_file: UploadFile = File(...), gst_file: UploadFile = File(None)):
    bank_bytes = await bank_file.read()
    gst_bytes = await gst_file.read() if gst_file else None
    
    # Process compliance rules
    verdict, checks = check_compliance_rules(bank_bytes, gst_bytes)
    
    business_id = None
    if verdict != "RED":
        try:
            import io
            import random
            df = pd.read_csv(io.BytesIO(bank_bytes))
            df.columns = [c.strip() for c in df.columns]
            
            # Extract basic metrics
            df["Credit"] = pd.to_numeric(df["Credit"], errors="coerce").fillna(0)
            df["Debit"] = pd.to_numeric(df["Debit"], errors="coerce").fillna(0)
            df["Running_Balance"] = pd.to_numeric(df["Running_Balance"], errors="coerce").fillna(0)
            
            total_credits = float(df["Credit"].sum())
            total_debits = float(df["Debit"].sum())
            avg_bal = float(df["Running_Balance"].mean())
            min_bal = float(df["Running_Balance"].min())
            
            # Calculate expense ratio
            expense_ratio = total_debits / max(1.0, total_credits)
            
            # Volatility
            credit_std = float(df["Credit"].std()) if len(df) > 1 else 0
            credit_mean = float(df["Credit"].mean()) if len(df) > 0 else 1
            volatility = credit_std / max(1.0, credit_mean)
            
            # Generate score based on actual metrics
            score_base = 75
            if expense_ratio < 0.85:
                score_base += 10
            elif expense_ratio > 0.95:
                score_base -= 15
                
            if min_bal > 40000:
                score_base += 5
            elif min_bal < 10000:
                score_base -= 10
                
            if volatility > 0.4:
                score_base -= 5
                
            score = max(30, min(95, int(score_base)))
            band = "Low" if score >= 80 else ("Medium" if score >= 60 else "High")
            
            # Unique ID
            rand_id = "".join(random.choices("0123456789", k=4))
            business_id = f"MSME_UP_{rand_id}"
            
            # Create a clean name
            name_base = bank_file.filename.replace(".csv", "").replace("_", " ").title()
            biz_name = f"{name_base}"
            
            # Determine industry based on file name or generic
            industry = "Retail Merchant"
            if "kirana" in bank_file.filename.lower():
                industry = "Kirana Store"
            elif "distributor" in bank_file.filename.lower():
                industry = "FMCG Distribution"
            elif "high_score" in bank_file.filename.lower():
                industry = "Agri-Processing"
            
            # Build monthly trends (mock trends scaled by actual averages)
            trends = []
            months = ["Jul", "Aug", "Sept", "Oct", "Nov", "Dec"]
            for idx, m in enumerate(months):
                trends.append({
                    "month": f"2025-{idx+7:02d}",
                    "revenue": int((total_credits / 6) * random.uniform(0.9, 1.1)),
                    "expense": int((total_debits / 6) * random.uniform(0.9, 1.1))
                })
                
            # Compute category performance scores
            # Calculate date delta in months (to vary gst_regularity)
            delta_months = 6
            if "Date" in df.columns:
                try:
                    df["Date"] = pd.to_datetime(df["Date"])
                    min_d = df["Date"].min()
                    max_d = df["Date"].max()
                    delta_months = (max_d.year - min_d.year) * 12 + (max_d.month - min_d.month)
                except Exception:
                    pass
            
            gst_regularity = min(1.0, max(0.5, delta_months / 12.0))
            
            # Digital payments ratio based on UPI/IMPS/NEFT/RTGS strings in Description
            digital_payment_ratio = 0.9
            if "Description" in df.columns:
                try:
                    digital_count = df["Description"].str.contains("UPI|IMPS|NEFT|RTGS|BharatPe|PhonePe|GPay|Paytm", case=False, na=False).sum()
                    digital_payment_ratio = min(1.0, max(0.4, float(digital_count / len(df))))
                except Exception:
                    pass
            
            # Revenue growth based on credit volume of second half vs first half
            revenue_growth = 0.05
            try:
                half = len(df) // 2
                if half > 0:
                    first_half_credits = df.iloc[:half]["Credit"].sum()
                    second_half_credits = df.iloc[half:]["Credit"].sum()
                    if first_half_credits > 0:
                        growth = (second_half_credits - first_half_credits) / first_half_credits
                        revenue_growth = min(0.4, max(-0.4, float(growth)))
            except Exception:
                pass
            
            # Scaled volatility (to prevent Stability rating from always being clamped to 0)
            scaled_volatility = min(0.95, max(0.05, volatility / 3.0))
            
            # Compute category performance scores
            cash_buffer_days = (avg_bal / max(1.0, total_debits / 180.0)) if total_debits > 0 else 15.0
            
            report_dict = {
                "eligibility_score": score,
                "risk_category": band,
                "verdict": "APPROVE" if score >= 75 else ("CONDITIONAL_APPROVAL" if score >= 55 else "REJECT"),
                "trends": trends,
                "metrics": {
                    "cash_buffer_days": round(cash_buffer_days, 1),
                    "income_volatility": round(scaled_volatility, 2),
                    "expense_ratio": round(expense_ratio, 2),
                    "bounce_count": 0.0,
                    "emi_ratio": 0.0,
                    "gst_regularity": round(gst_regularity, 2),
                    "digital_payment_ratio": round(digital_payment_ratio, 2),
                    "revenue_growth": round(revenue_growth, 2),
                    "monthly_savings_rate": 0.15,
                    "average_balance": round(avg_bal, 2),
                    "minimum_balance": round(min_bal, 2)
                },
                "gst_analysis": {
                    "annual_turnover": int(total_credits * 2),
                    "filing_regularity": 1.0
                },
                "ml_scoring": {
                    "feature_contributions": {
                        "Expense_to_income_ratio": -15.0 if expense_ratio > 0.9 else 15.0,
                        "GST_regularity": 10.0,
                        "Cash_buffer_days": 10.0,
                        "Minimum_balance": -10.0 if min_bal < 10000 else 5.0
                    }
                }
            }
            
            # Save to SQLite custom_businesses database
            add_custom_business(
                business_id=business_id,
                name=biz_name,
                industry=industry,
                score=score,
                band=band,
                data_json=json.dumps(report_dict)
            )
            
            # Log audit event
            add_audit_event(
                event_type="intake", 
                business_id=business_id, 
                business_name=biz_name,
                summary=f"Alternate statement uploaded & auto-analyzed. Compliance: {verdict}. Score: {score}/100.",
                actor="System (Intake Engine)"
            )
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            business_id = None

    return {
        "verdict": verdict,
        "checks": checks,
        "business_id": business_id
    }

@app.post("/api/v1/evaluate")
async def evaluate_credit_risk(msme_input: MSMEInput):
    try:
        report = await evaluate_msme(msme_input)
        
        # Convert report Pydantic model to dictionary resolving date/datetime types
        if hasattr(report, "model_dump_json"):
            report_dict = json.loads(report.model_dump_json())
        elif hasattr(report, "json"):
            report_dict = json.loads(report.json())
        elif hasattr(report, "model_dump"):
            report_dict = report.model_dump()
        else:
            report_dict = report

        # Extract business parameters for persistence
        business_id = msme_input.gstin
        score = int(report_dict.get("financial_health_score", 70))
        band_val = report_dict.get("risk_category", "Medium")
        band = band_val.value if hasattr(band_val, "value") else str(band_val)
        
        # Determine industry and business name
        industry = "Manufacturing"
        if msme_input.gst_data and msme_input.gst_data.gstin:
            industry = "alternate alternate" # Default or lookup if possible
        
        # Get industry from gst_analysis if present
        gst_analysis = report_dict.get("gst_analysis", {})
        if gst_analysis and isinstance(gst_analysis, dict):
            # Parse or extract
            pass

        # Save to SQLite custom_businesses database
        add_custom_business(
            business_id=business_id,
            name=f"MSME Connected Client ({business_id})",
            industry=industry,
            score=score,
            band=band,
            data_json=json.dumps(report_dict)
        )
        
        # Log to SQLite audit events
        add_audit_event(
            event_type="score", 
            business_id=business_id, 
            business_name=f"MSME Connected Client ({business_id})",
            summary=f"Alternate data connected & credit evaluation run. Score: {score}/100 ({band} Risk)",
            actor="System (Unified)"
        )
        
        return report
    except HTTPException:
        raise
    except Exception:
        # Log the traceback server-side but do not leak it to clients.
        logger.exception("Unhandled error in endpoint")
        raise HTTPException(status_code=500, detail="Internal server error")


from pydantic import EmailStr, Field, field_validator


class QuickRegisterRequest(BaseModel):
    business_name: str = Field(min_length=1, max_length=200)
    owner_name: str = Field(min_length=1, max_length=200)
    mobile_number: str
    email: EmailStr
    pan_number: str
    gstin: Optional[str] = None
    udyam_number: Optional[str] = None
    business_type: str
    industry: str
    years_in_business: int = Field(ge=0, le=100)
    loan_amount_required: float = Field(gt=0, le=1_000_000_000)
    loan_purpose: str

    # Connection statuses
    connect_gst: bool = False
    connect_aa: bool = False
    connect_upi: bool = False
    connect_epfo: bool = False

    # Fallback file names (simulating uploads)
    upload_pan: Optional[str] = None
    upload_aadhaar: Optional[str] = None
    upload_udyam: Optional[str] = None
    upload_bank: Optional[str] = None

    @field_validator("mobile_number")
    @classmethod
    def _validate_mobile(cls, v: str) -> str:
        digits = re.sub(r"\D", "", v)
        if len(digits) < 10 or len(digits) > 15:
            raise ValueError("mobile_number must contain 10–15 digits")
        return digits


@app.post("/api/intake/register")
async def register_msme_application(req: QuickRegisterRequest):
    try:
        # Registration date derived deterministically from stated vintage.
        # Clamp `years_in_business` to a sane range so `date()` cannot raise on absurd inputs.
        years = max(1, min(int(req.years_in_business), 100))
        reg_year = datetime.now(timezone.utc).year - years
        reg_date = date(reg_year, 1, 15)

        # Reject invalid PAN / GSTIN outright instead of silently substituting a
        # fabricated identity into the audit trail.
        pan = req.pan_number.strip().upper()
        if not re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]$", pan):
            raise HTTPException(
                status_code=400,
                detail="Invalid PAN format (expected ABCDE1234F)."
            )

        if req.gstin:
            gstin = req.gstin.strip().upper()
            if not re.match(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][A-Z0-9]{3}$", gstin):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid GSTIN format."
                )
        else:
            # No GSTIN provided — derive a stable placeholder tied to PAN so the
            # applicant record has a unique key. This is not presented as verified.
            gstin = f"27{pan}1Z5"

        # Track whether each data source is a real live-connected feed or an
        # estimate derived from stated inputs. Officers see this in the report
        # so they can distinguish "verified" from "self-declared" data.
        data_provenance = {
            "gst": "connected" if req.connect_gst else ("uploaded" if req.upload_pan else "estimated"),
            "aa": "connected" if req.connect_aa else ("uploaded" if req.upload_bank else "estimated"),
            "upi": "connected" if req.connect_upi else "estimated",
            "epfo": "connected" if req.connect_epfo else "estimated",
        }

        # 1. GST returns & turnover — derived deterministically from stated loan
        # requirement (a proxy for capacity). No random noise: same input yields
        # the same output, and the officer can see the derivation is a heuristic.
        annual_turnover = float(req.loan_amount_required) * 2.5
        avg_monthly_rev = annual_turnover / 12

        # Flat monthly figures — we do NOT invent seasonality we cannot verify.
        monthly_revs = [round(avg_monthly_rev, 2)] * 12

        filing_hist = [True] * 12
        if not req.connect_gst:
            # Un-connected GST means we have no filing history to attest to;
            # mark two months as missing so the risk agent penalizes appropriately.
            filing_hist[4] = False
            filing_hist[8] = False

        gst_data = GSTData(
            gstin=gstin,
            monthly_revenue=monthly_revs,
            filing_history=filing_hist,
            annual_turnover=round(annual_turnover, 2)
        )

        # 2. Account Aggregator Data — deterministic derivation.
        # Buffer % encodes how much we trust the cash position: full AA > uploaded bank stmt > self-declared.
        buffer_pct = 0.18 if req.connect_aa else (0.12 if req.upload_bank else 0.05)
        balances = [round(avg_monthly_rev * buffer_pct, 2)] * 3
        # Flat inflow ≈ revenue, flat outflow ≈ 90% of revenue.
        inflows = [round(avg_monthly_rev, 2)] * 6
        outflows = [round(avg_monthly_rev * 0.9, 2)] * 6

        statement_start = date.today() - timedelta(days=120)
        statement_end = date.today() - timedelta(days=1)

        aa_data = AccountAggregatorData(
            month_end_balances=balances,
            monthly_inflows=inflows,
            monthly_outflows=outflows,
            statement_start_date=statement_start,
            statement_end_date=statement_end
        )

        # 3. EPFO Data — flat employee count per band; connected feeds get slight
        # ramp to reflect that real data would show hiring over time.
        emp_counts = [15] * 12
        if req.connect_epfo:
            emp_counts = [12, 12, 12, 13, 13, 14, 14, 14, 15, 15, 16, 16]
        epfo_data = EPFOData(
            monthly_employee_counts=emp_counts
        )

        # 4. UPI transactions — the *count* signals digital adoption. Use a fixed
        # per-txn amount tied to revenue so the aggregate makes sense; timestamps
        # are evenly spaced across the last 90 days.
        upi_txs = []
        start_dt = datetime.now(timezone.utc) - timedelta(days=90)
        counterparties = [
            "Zomato Pay", "Swiggy UPI", "Vendor A", "Client X",
            "Fuel Station", "Raw Materials Ltd", "Rent Account",
        ]
        tx_count = 45 if req.connect_upi else 15
        per_tx_amount = round(max(500.0, avg_monthly_rev / max(tx_count, 1) * 3), 2)
        for i in range(tx_count):
            tx_date = start_dt + timedelta(days=(90 * i) / max(tx_count, 1))
            upi_txs.append(UPITransaction(
                amount=per_tx_amount,
                timestamp=tx_date,
                counterparty=counterparties[i % len(counterparties)],
            ))

        # 5. Bank EMI — we cannot know existing loan status without real data.
        # Assume zero and let officer/data-connect override; do NOT flip a coin.
        total_monthly_emi = 0.0
        # Stable account-number placeholder derived from PAN so re-registration
        # is idempotent instead of getting a new random number every call.
        pan_hash = abs(hash(pan)) % 900000 + 100000
        bank_data = BankData(
            total_monthly_emi=total_monthly_emi,
            loan_amounts=[],
            account_number=f"IDBI-{pan_hash}"
        )
        
        # Construct main evaluate input
        msme_input = MSMEInput(
            gstin=gstin,
            pan=pan,
            business_registration_date=reg_date,
            gst_data=gst_data,
            upi_transactions=upi_txs,
            account_aggregator_data=aa_data,
            epfo_data=epfo_data,
            bank_data=bank_data
        )
        
        # Execute workflow directly (in-process) via the risk intelligence agent.
        # NOTE: We intentionally do NOT make an HTTP call to ourselves here — doing so
        # would deadlock uvicorn by consuming the only available worker thread.
        report = await evaluate_msme(msme_input)
        print("[OK] Risk evaluation complete via direct in-process evaluate_msme() call")
        
        # Convert report Pydantic model to dictionary resolving date/datetime types
        if hasattr(report, "model_dump_json"):
            report_dict = json.loads(report.model_dump_json())
        elif hasattr(report, "json"):
            report_dict = json.loads(report.json())
        elif hasattr(report, "model_dump"):
            report_dict = report.model_dump()
        else:
            report_dict = report
            
        # Store as custom business in SQLite
        business_id = gstin
        score = int(report_dict.get("financial_health_score", 70))
        band_val = report_dict.get("risk_category", "MEDIUM")
        band = band_val.value if hasattr(band_val, "value") else str(band_val)
        
        # Save details including Name and Industry from request
        save_data = {
            "report": report_dict,
            "business_name": req.business_name,
            "owner_name": req.owner_name,
            "mobile_number": req.mobile_number,
            "email": req.email,
            "pan_number": req.pan_number,
            "gstin": req.gstin,
            "udyam_number": req.udyam_number,
            "business_type": req.business_type,
            "industry": req.industry,
            "years_in_business": req.years_in_business,
            "loan_amount_required": req.loan_amount_required,
            "loan_purpose": req.loan_purpose,
            "connect_gst": req.connect_gst,
            "connect_aa": req.connect_aa,
            "connect_upi": req.connect_upi,
            "connect_epfo": req.connect_epfo,
            "data_provenance": data_provenance,
        }
        add_custom_business(
            business_id=business_id,
            name=req.business_name,
            industry=req.industry,
            score=score,
            band=band,
            data_json=json.dumps(save_data)
        )

        # Log to SQLite audit events. The summary now records how much of the
        # input was truly connected vs estimated so the audit trail cannot be
        # misread as "verified data" when it wasn't.
        connected_count = sum(1 for v in data_provenance.values() if v == "connected")
        add_audit_event(
            event_type="score",
            business_id=business_id,
            business_name=req.business_name,
            summary=(
                f"Data evaluation complete. Score: {score}/100 ({band} Risk). "
                f"Sources connected: {connected_count}/4 "
                f"(gst={data_provenance['gst']}, aa={data_provenance['aa']}, "
                f"upi={data_provenance['upi']}, epfo={data_provenance['epfo']})"
            ),
            actor="System (Unified)"
        )

        return {
            "business_id": business_id,
            "score": score,
            "band": band,
            "report": report_dict,
            "data_provenance": data_provenance,
        }

    except HTTPException:
        # Preserve 4xx client errors — do not repackage them as opaque 500s.
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Do not leak raw exception text to clients.
        raise HTTPException(status_code=500, detail="Internal error during registration.")


# Load score_inference dynamically to resolve IDE static analysis warnings
# Temporarily disabled due to pickle version mismatch
# import importlib.util
# spec = importlib.util.spec_from_file_location("score_inference", os.path.join(DATASET_DIR, "score_inference.py"))
# score_inference = importlib.util.module_from_spec(spec)
# sys.modules["score_inference"] = score_inference
# spec.loader.exec_module(score_inference)
# predict_business = score_inference.predict_business

# Placeholder function for now
def predict_business(business_data):
    """Placeholder for ML prediction - returns mock score"""
    return {
        "business_id": business_data,
        "score": 72,
        "band": "Medium",
        "factors": [
            {"name": "GST_Regularity_Score", "label": "GST Regularity", "direction": "+", "weight": 0.4, "detail": "Perfect 12/12 GST filings verified."},
            {"name": "Cash_Buffer_Days", "label": "Cash Buffer", "direction": "+", "weight": 0.3, "detail": "Cash buffer covers 15 days."},
            {"name": "Bounce_Count", "label": "Bounce Count", "direction": "-", "weight": 0.3, "detail": "Zero cheque bounces."},
            {"name": "Digital_Payment_Ratio", "label": "Digital Payments share", "direction": "+", "weight": 0.2, "detail": "90% of transactions are digital (UPI/NEFT)."},
            {"name": "Revenue_Growth", "label": "Revenue growth", "direction": "+", "weight": 0.1, "detail": "Revenue grew +12% YoY."}
        ]
    }


class CopilotRequest(BaseModel):
    business_id: str
    message: str

class DecisionRequest(BaseModel):
    business_id: str
    status: str
    remarks: str

@app.get("/api/business/{business_id}")
def business_detail(business_id: str, _: UserInfo = Depends(get_current_user)):
    # Check if this is a custom registered business first
    custom_biz = get_custom_business_detail(business_id)
    if custom_biz:
        save_data = json.loads(custom_biz["data_json"])
        
        # Backwards compatibility check
        if "report" in save_data:
            report_dict = save_data["report"]
        else:
            report_dict = save_data
            
        # Read decision
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status, remarks FROM officer_decisions WHERE business_id = ?", (business_id,))
        row = cursor.fetchone()
        conn.close()
        
        officer_status = row["status"] if row else "Pending"
        
        score = int(round(float(report_dict.get("financial_health_score", 70))))
        band_val = report_dict.get("risk_category", "Medium")
        band = band_val.value if hasattr(band_val, "value") else str(band_val)
        
        # Build factors from report features or use clean defaults
        factors = []
        if "top_features" in report_dict:
            for feat in report_dict["top_features"]:
                factors.append({
                    "name": feat.get("feature_name", ""),
                    "label": feat.get("feature_name", "").replace("_", " "),
                    "direction": "+" if feat.get("shap_value", 0) >= 0 else "-",
                    "weight": abs(feat.get("shap_value", 0)),
                    "detail": f"{feat.get('feature_name', '').replace('_', ' ')}: value {feat.get('feature_value', 0):.2f}"
                })
        elif "ml_scoring" in report_dict and "feature_contributions" in report_dict["ml_scoring"]:
            contribs = report_dict["ml_scoring"]["feature_contributions"]
            for col, val in contribs.items():
                factors.append({
                    "name": col,
                    "label": col.replace("_", " "),
                    "direction": "+" if val >= 0 else "-",
                    "weight": abs(val),
                    "detail": f"{col.replace('_', ' ')} is {val:.2f}."
                })
        else:
            factors = [
                {"name": "GST_Regularity_Score", "label": "GST Regularity", "direction": "+", "weight": 0.4, "detail": "Perfect 12/12 GST filings verified."},
                {"name": "Cash_Buffer_Days", "label": "Cash Buffer", "direction": "+", "weight": 0.3, "detail": "Cash buffer covers 15 days."},
                {"name": "Bounce_Count", "label": "Bounce Count", "direction": "-", "weight": 0.3, "detail": "Zero cheque bounces."}
            ]
            
        # Map month trends (use saved trends if available, else generate from loan amount)
        trends = report_dict.get("trends", [])
        if not trends:
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            loan_amount_req = save_data.get("loan_amount_required", 1500000.0)
            rev_base = (loan_amount_req * 2.5) / 12
            for idx, m in enumerate(months):
                trends.append({
                    "month": f"2025-{idx+1:02d}",
                    "revenue": int(rev_base * (1.0 + (0.05 * (idx % 3 - 1)))),
                    "expense": int(rev_base * 0.8 * (1.0 + (0.02 * (idx % 2 - 0.5))))
                })
        
        # Determine average monthly revenue from trends
        avg_revenue = 500000.0
        if trends:
            avg_revenue = sum(t["revenue"] for t in trends) / len(trends)
            
        annual_turnover = report_dict.get("gst_analysis", {}).get("annual_turnover", avg_revenue * 12)
        
        metrics = report_dict.get("metrics", {})
        if not metrics or all(v == 0 for v in metrics.values() if isinstance(v, (int, float))):
            connect_gst = save_data.get("connect_gst", False)
            connect_aa = save_data.get("connect_aa", False)
            connect_upi = save_data.get("connect_upi", False)
            rev_base_calc = (save_data.get("loan_amount_required", 1500000.0) * 2.5) / 12
            
            metrics = {
                "cash_buffer_days": 18.0 if connect_aa else (12.0 if save_data.get("upload_bank") else 5.0),
                "income_volatility": 0.12,
                "expense_ratio": 0.78,
                "bounce_count": 0.0,
                "emi_ratio": 0.0,
                "gst_regularity": 1.0 if connect_gst else 0.83,
                "digital_payment_ratio": 0.95 if connect_upi else 0.60,
                "revenue_growth": 0.15,
                "monthly_savings_rate": 0.22,
                "average_balance": int(rev_base_calc * 0.15),
                "minimum_balance": int(rev_base_calc * 0.05)
            }
            
        # Get dynamic profile details
        profile = get_dynamic_profile(business_id, custom_biz["name"], annual_turnover, avg_revenue, score)
        
        return {
            "business_id": business_id,
            "profile": {
                "name": custom_biz["name"],
                "owner": save_data.get("owner_name", profile["owner"]),
                "industry": custom_biz["industry"],
                "city": profile["city"],
                "state": profile["state"],
                "business_age_years": save_data.get("years_in_business", profile["business_age_years"]),
                "employee_count": profile["employee_count"],
                "category": profile["category"],
                "gst_registered": True if save_data.get("gstin") else False,
                "existing_loan": False,
                "existing_emi": 0,
                "annual_turnover": annual_turnover
            },
            "score": {
                "score": score,
                "band": band,
                "confidence": 0.95
            },
            "factors": factors[:5],
            "recommendation": {
                "loan_amount": profile["loan_amount"],
                "tenure_months": 24 if score >= 65 else 12,
                "interest_band": "10.5% - 12.5%" if score >= 80 else ("12.5% - 14.5%" if score >= 65 else "14.5% - 16.5%"),
                "decision": "Approve" if score >= 75 else ("Conditional Approval" if score >= 55 else "Reject")
            },
            "trends": trends,
            "gst_timeline": [],
            "metrics": metrics,
            "officer_status": officer_status,
            "applied_at": custom_biz["applied_at"][:10]
        }

    # Confirm the id exists in the seeded feature set BEFORE we index it.
    # Previously the code relied on `predict_business` raising ValueError — it
    # never does, so an unknown id fell through to `iloc[0]` on an empty
    # DataFrame → IndexError → generic 500 instead of a clean 404.
    if FEAT_DF is None or "Business_ID" not in FEAT_DF.columns or business_id not in set(FEAT_DF["Business_ID"]):
        raise HTTPException(status_code=404, detail=f"Business {business_id} not found")

    scoring = predict_business(business_id)
    biz_row = FEAT_DF[FEAT_DF["Business_ID"] == business_id].iloc[0]
    
    # Read decision
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status, remarks FROM officer_decisions WHERE business_id = ?", (business_id,))
    row = cursor.fetchone()
    conn.close()
    
    officer_status = row["status"] if row else "Pending"

    # Map month trends (mock trends based on actual averages)
    trends = []
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    rev_base = float(biz_row["Average_Monthly_Revenue"])
    exp_base = float(biz_row["Average_Monthly_Expense"])
    for idx, m in enumerate(months):
        var = 1.0 + (0.05 * (idx % 3 - 1))
        trends.append({
            "month": f"2025-{idx+1:02d}",
            "revenue": int(rev_base * var),
            "expense": int(exp_base * (1.0 + (0.02 * (idx % 2 - 0.5))))
        })

    # Map GST timeline
    gst_timeline = []
    gst_regularity_score = float(biz_row["GST_Regularity_Score"])
    on_time_count = round(gst_regularity_score * 12)
    for idx, m in enumerate(months):
        is_on_time = idx < on_time_count
        late_days = 0 if is_on_time else (idx % 4 + 1) * 3
        filing_date = f"2025-{idx+1:02d}-20" if is_on_time else f"2025-{idx+1:02d}-{20 + late_days}"
        gst_timeline.append({
            "month": f"2025-{idx+1:02d}",
            "filed_on_time": is_on_time,
            "late_days": late_days,
            "filing_date": filing_date,
            "sales": int(rev_base * (1.0 + (0.03 * (idx % 3 - 1))))
        })

    return {
        "business_id": business_id,
        "profile": {
            "name": biz_row["Business_Name"],
            "owner": "Ayesha Mehta",
            "industry": biz_row["Industry"],
            "city": "Mumbai",
            "state": "Maharashtra",
            "business_age_years": 8,
            "employee_count": 5,
            "category": "Micro",
            "gst_registered": True,
            "existing_loan": False,
            "existing_emi": 0,
            "annual_turnover": float(biz_row["Average_Monthly_Revenue"]) * 12
        },
        "score": {
            "score": scoring["score"],
            "band": scoring["band"],
            "confidence": 0.95
        },
        "factors": scoring["factors"],
        "recommendation": {
            "loan_amount": int(biz_row["Average_Monthly_Revenue"] * 3),
            "tenure_months": 24,
            "interest_band": "10.5% - 12.5%",
            "decision": "Approve" if scoring["score"] >= 75 else ("Conditional Approval" if scoring["score"] >= 55 else "Reject")
        },
        "trends": trends,
        "gst_timeline": gst_timeline,
        "metrics": {
            "cash_buffer_days": float(biz_row["Cash_Buffer_Days"]),
            "income_volatility": float(biz_row["Income_Volatility"]),
            "expense_ratio": float(biz_row["Expense_Ratio"]),
            "bounce_count": float(biz_row["Bounce_Count"]),
            "emi_ratio": float(biz_row["EMI_Ratio"]),
            "gst_regularity": float(biz_row["GST_Regularity_Score"]),
            "digital_payment_ratio": float(biz_row["Digital_Payment_Ratio"]),
            "revenue_growth": float(biz_row["Revenue_Growth"]),
            "monthly_savings_rate": float(biz_row["Monthly_Savings_Rate"]),
            "average_balance": float(biz_row["Average_Balance"]),
            "minimum_balance": float(biz_row["Minimum_Balance"])
        },
        "officer_status": officer_status,
        "applied_at": "2026-06-30"
    }

@app.post("/api/copilot")
def copilot_query(req: CopilotRequest, _: UserInfo = Depends(get_current_user)):
    # Retrieve scoring details to use as grounding context
    custom_biz = get_custom_business_detail(req.business_id)
    if custom_biz:
        report_dict = json.loads(custom_biz["data_json"])
        
        # Build factors from report features or use clean defaults
        factors = []
        if "ml_scoring" in report_dict and "feature_contributions" in report_dict["ml_scoring"]:
            contribs = report_dict["ml_scoring"]["feature_contributions"]
            for col, val in contribs.items():
                factors.append({
                    "name": col,
                    "label": col.replace("_", " "),
                    "direction": "+" if val >= 0 else "-",
                    "weight": abs(val),
                    "detail": f"{col.replace('_', ' ')} is {val:.2f}."
                })
        else:
            factors = [
                {"name": "GST_Regularity_Score", "label": "GST Regularity", "direction": "+", "weight": 0.4, "detail": "Perfect 12/12 GST filings verified."},
                {"name": "Cash_Buffer_Days", "label": "Cash Buffer", "direction": "+", "weight": 0.3, "detail": "Cash buffer covers 15 days."},
                {"name": "Bounce_Count", "label": "Bounce Count", "direction": "-", "weight": 0.3, "detail": "Zero cheque bounces."}
            ]
            
        scoring = {
            "score": int(custom_biz["score"]),
            "band": custom_biz["band"],
            "factors": factors
        }
    else:
        try:
            scoring = predict_business(req.business_id)
        except ValueError:
            raise HTTPException(status_code=404, detail=f"Business {req.business_id} not found")
    
    system_prompt = f"""
    You are the Credit Copilot for IDBI MSME360. Explain the financial score of this business.
    Grounding Context:
    Business ID: {req.business_id}
    Model Score: {scoring['score']} / 100 ({scoring['band']} Risk)
    SHAP Factors: {json.dumps(scoring['factors'])}
    
    Guidelines:
    - Cite factor names exactly as inline tags e.g. [Cash buffer].
    - Ground your response strictly in the provided factors. Do not invent any numbers.
    - Decline out-of-scope questions about the stock market or unrelated topics.
    """
    
    # Call our LLM adapter
    answer = call_llm(system_prompt, req.message)
    
    # Log to SQLite audit events
    add_audit_event("copilot", req.business_id, "MSME Business", f"Copilot query: {req.message}", {"query": req.message, "response": answer})
    
    return {"answer": answer}

ALLOWED_DECISION_STATUSES = {"Approved", "Conditional", "Rejected", "Info Requested", "Pending"}

def _business_exists(business_id: str) -> bool:
    """True if business_id is either a seeded MSME (in FEAT_DF) or a custom
    registration in SQLite. Used to reject orphan decision/audit writes."""
    if get_custom_business_detail(business_id) is not None:
        return True
    try:
        if FEAT_DF is not None and "Business_ID" in FEAT_DF.columns:
            return business_id in set(FEAT_DF["Business_ID"])
    except NameError:
        pass
    return False


@app.post("/api/decision")
def save_decision(req: DecisionRequest, _: UserInfo = Depends(require_officer)):
    if req.status not in ALLOWED_DECISION_STATUSES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid status '{req.status}'. Allowed: {sorted(ALLOWED_DECISION_STATUSES)}"
        )
    if not _business_exists(req.business_id):
        # No orphan decisions — writing a status for a nonexistent business would
        # let any caller create fake audit trail entries via the IDOR path.
        raise HTTPException(status_code=404, detail=f"Business {req.business_id} not found")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        ts = datetime.now(timezone.utc).isoformat()
        cursor.execute(
            "INSERT OR REPLACE INTO officer_decisions VALUES (?, ?, ?, ?)",
            (req.business_id, req.status, req.remarks, ts)
        )
        conn.commit()
    finally:
        conn.close()

    add_audit_event(
        "decision", req.business_id, "MSME Business",
        f"Decision saved: {req.status}. Remarks: {req.remarks}"
    )
    return {"status": "success"}

@app.get("/api/audit")
def get_audit_trail(_: UserInfo = Depends(require_officer)):
    return get_audit_events()


# ============================================================================
# CREDITPILOT AI UNIFIED ENDPOINTS
# ============================================================================

@app.post("/api/creditpilot/analyze")
async def creditpilot_analyze(
    business_id: str,
    bank_file: UploadFile = File(...),
    _current_user: UserInfo = Depends(require_officer),
    gst_file: UploadFile = File(None),
    msme_data: str = Form(...)  # JSON string of MSMEInput data
):
    """
    Unified CreditPilot AI Endpoint
    
    Orchestrates all three agents:
    1. Financial Intelligence Agent (validates data)
    2. Risk Intelligence Agent (assesses risk)
    3. CreditPilot Copilot (provides conversational interface)
    
    Returns complete analysis with agent attribution.
    """
    try:
        # Read uploaded files
        bank_bytes = await bank_file.read()
        gst_bytes = await gst_file.read() if gst_file else None
        
        # Parse MSME data
        msme_input_dict = json.loads(msme_data)
        
        # Get orchestrator
        orchestrator = get_orchestrator()
        
        # Run complete analysis
        analysis = await orchestrator.analyze_msme(
            business_id=business_id,
            bank_csv_bytes=bank_bytes,
            gst_csv_bytes=gst_bytes,
            msme_input_data=msme_input_dict
        )
        
        # Save to database
        score = analysis.summary.get("financial_health_score", 70)
        band = analysis.summary.get("risk_category", "Medium")
        
        add_custom_business(
            business_id=business_id,
            name=f"MSME Client ({business_id})",
            industry="Manufacturing",
            score=score,
            band=band,
            data_json=json.dumps(analysis.model_dump())
        )
        
        # Log audit event
        add_audit_event(
            event_type="creditpilot_analysis",
            business_id=business_id,
            business_name=f"MSME Client ({business_id})",
            summary=f"CreditPilot AI analyzed application. Score: {score}/100 ({band} Risk)",
            actor="CreditPilot AI System"
        )
        
        return analysis
        
    except HTTPException:
        raise
    except Exception:
        # Log the traceback server-side but do not leak it to clients.
        logger.exception("Unhandled error in endpoint")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/creditpilot/chat")
async def creditpilot_chat(req: ConversationRequest, _: UserInfo = Depends(get_current_user)):
    """
    CreditPilot AI Conversational Interface
    
    Handles natural language queries like:
    - "Analyze this MSME"
    - "Why did you recommend ₹18.5 lakh?"
    - "Generate Credit Memo"
    - "Compare with similar businesses"
    - "Scenario Analysis: What if we reduce to ₹15 lakh?"
    
    Returns answer with agent attribution and suggested follow-ups.
    """
    try:
        # Get conversation handler
        conversation = get_conversation_handler()
        
        # Get analysis context (from database or context parameter)
        if req.context:
            analysis_context = req.context
        else:
            # Try to load from database
            custom_biz = get_custom_business_detail(req.business_id)
            if custom_biz:
                analysis_context = json.loads(custom_biz["data_json"])
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"No analysis found for business {req.business_id}. Run /api/creditpilot/analyze first."
                )
        
        # Handle query
        response = await conversation.handle_query(
            business_id=req.business_id,
            query=req.query,
            analysis_context=analysis_context
        )
        
        # Log audit event
        add_audit_event(
            event_type="creditpilot_chat",
            business_id=req.business_id,
            business_name=f"MSME Client ({req.business_id})",
            summary=f"Query: {req.query[:100]}",
            actor="Credit Officer",
            metadata={"query": req.query, "answer": response.answer[:200]}
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception:
        # Log the traceback server-side but do not leak it to clients.
        logger.exception("Unhandled error in endpoint")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/creditpilot/status/{business_id}")
def creditpilot_status(business_id: str, _: UserInfo = Depends(get_current_user)):
    """
    Get CreditPilot analysis status for a business.
    
    Returns whether analysis is available and summary if it exists.
    """
    custom_biz = get_custom_business_detail(business_id)
    
    if not custom_biz:
        return {
            "business_id": business_id,
            "analyzed": False,
            "message": "No CreditPilot analysis found. Upload documents to analyze."
        }
    
    analysis_data = json.loads(custom_biz["data_json"])
    
    return {
        "business_id": business_id,
        "analyzed": True,
        "timestamp": analysis_data.get("timestamp"),
        "score": custom_biz["score"],
        "risk_category": custom_biz["band"],
        "recommendation": analysis_data.get("recommendation", {}).get("action"),
        "request_id": analysis_data.get("request_id")
    }
