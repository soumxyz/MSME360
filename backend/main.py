from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import sys
import json
from pydantic import BaseModel
from datetime import datetime, timezone

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
from agents.risk_intelligence_agent.schemas import MSMEInput

app = FastAPI(title="MSME Credit Workspace Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for easier local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
init_db()

@app.get("/api/health")
def health():
    return {"status": "healthy"}


DATASET_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Dataset")

# Dataset CSVs are static for the lifetime of the server — load once instead of per request
FEAT_DF = pd.read_csv(os.path.join(DATASET_DIR, "engineered_features.csv"))
LBL_DF = pd.read_csv(os.path.join(DATASET_DIR, "credit_labels.csv"))

@app.get("/api/portfolio")
def portfolio():
    merged = FEAT_DF.merge(LBL_DF[["Business_ID", "Financial_Health_Score", "Risk_Category", "Confidence"]], on="Business_ID")
    
    # Query decisions from local SQLite DB
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT business_id, status FROM officer_decisions")
    decisions = {r["business_id"]: r["status"] for r in cursor.fetchall()}
    conn.close()

    rows = []
    
    # Add custom businesses from SQLite first so they appear at the top of the queue!
    custom_list = get_custom_businesses()
    for c in custom_list:
        bid = c["business_id"]
        status = decisions.get(bid, "Pending")
        rows.append({
            "business_id": bid,
            "name": c["name"],
            "industry": c["industry"],
            "city": "Mumbai",
            "state": "Maharashtra",
            "category": "Micro",
            "gst_registered": True,
            "score": int(c["score"]),
            "band": c["band"],
            "confidence": 0.95,
            "avg_monthly_revenue": 500000.0,
            "model_decision": "Approve" if c["score"] >= 75 else ("Conditional Approval" if c["score"] >= 55 else "Reject"),
            "officer_status": status,
            "applied_at": c["applied_at"][:10]
        })

    # Add standard dataset rows
    for _, row in merged.iterrows():
        bid = row["Business_ID"]
        status = decisions.get(bid, "Pending")
        
        status_map = {
            "Approved": "Approved",
            "Conditional": "Conditional",
            "Rejected": "Rejected",
            "Info Requested": "Info Requested"
        }
        officer_status = status_map.get(status, "Pending")

        rows.append({
            "business_id": bid,
            "name": row["Business_Name"],
            "industry": row["Industry"],
            "city": "Mumbai",
            "state": "Maharashtra",
            "category": "Micro",
            "gst_registered": True,
            "score": int(row["Financial_Health_Score"]),
            "band": row["Risk_Category"],
            "confidence": float(row["Confidence"]),
            "avg_monthly_revenue": float(row["Average_Monthly_Revenue"]),
            "model_decision": "Approve" if row["Financial_Health_Score"] >= 75 else ("Conditional Approval" if row["Financial_Health_Score"] >= 55 else "Reject"),
            "officer_status": officer_status,
            "applied_at": "2026-06-30"
        })
    return rows

@app.post("/api/intake")
async def upload_intake(bank_file: UploadFile = File(...), gst_file: UploadFile = File(None)):
    bank_bytes = await bank_file.read()
    gst_bytes = await gst_file.read() if gst_file else None
    
    # Process compliance rules
    verdict, checks = check_compliance_rules(bank_bytes, gst_bytes)
    
    return {
        "verdict": verdict,
        "checks": checks
    }

@app.post("/api/v1/evaluate")
async def evaluate_credit_risk(msme_input: MSMEInput):
    try:
        report = await evaluate_msme(msme_input)
        
        # Convert report Pydantic model to dictionary
        if hasattr(report, "model_dump"):
            report_dict = report.model_dump()
        elif hasattr(report, "dict"):
            report_dict = report.dict()
        else:
            report_dict = report

        # Extract business parameters for persistence
        business_id = msme_input.msme_id
        score = int(report_dict.get("eligibility_score", 70))
        band = report_dict.get("risk_category", "Medium")
        
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
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Load score_inference dynamically to resolve IDE static analysis warnings
import importlib.util
spec = importlib.util.spec_from_file_location("score_inference", os.path.join(DATASET_DIR, "score_inference.py"))
score_inference = importlib.util.module_from_spec(spec)
sys.modules["score_inference"] = score_inference
spec.loader.exec_module(score_inference)
predict_business = score_inference.predict_business


class CopilotRequest(BaseModel):
    business_id: str
    message: str

class DecisionRequest(BaseModel):
    business_id: str
    status: str
    remarks: str

@app.get("/api/business/{business_id}")
def business_detail(business_id: str):
    # Check if this is a custom registered business first
    custom_biz = get_custom_business_detail(business_id)
    if custom_biz:
        report_dict = json.loads(custom_biz["data_json"])
        
        # Read decision
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status, remarks FROM officer_decisions WHERE business_id = ?", (business_id,))
        row = cursor.fetchone()
        conn.close()
        
        officer_status = row["status"] if row else "Pending"
        
        score = report_dict.get("eligibility_score", 70)
        band = report_dict.get("risk_category", "Medium")
        
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
            
        # Map month trends (mock trends based on actual averages)
        trends = []
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        for idx, m in enumerate(months):
            trends.append({
                "month": f"2025-{idx+1:02d}",
                "revenue": 500000 + (idx % 3) * 50000,
                "expense": 400000 + (idx % 2) * 20000
            })
            
        return {
            "business_id": business_id,
            "profile": {
                "name": custom_biz["name"],
                "owner": "Ayesha Mehta",
                "industry": custom_biz["industry"],
                "city": "Mumbai",
                "state": "Maharashtra",
                "business_age_years": 5,
                "employee_count": 8,
                "category": "Micro",
                "gst_registered": True,
                "existing_loan": False,
                "existing_emi": 0,
                "annual_turnover": 6000000
            },
            "score": {
                "score": score,
                "band": band,
                "confidence": 0.95
            },
            "factors": factors[:5],
            "recommendation": {
                "loan_amount": 1500000,
                "tenure_months": 24,
                "interest_band": "10.5% - 12.5%",
                "decision": "Approve" if score >= 75 else ("Conditional Approval" if score >= 55 else "Reject")
            },
            "trends": trends,
            "gst_timeline": [],
            "metrics": {
                "cash_buffer_days": 15.0,
                "income_volatility": 0.12,
                "expense_ratio": 0.8,
                "bounce_count": 0.0,
                "emi_ratio": 0.0,
                "gst_regularity": 1.0,
                "digital_payment_ratio": 0.9,
                "revenue_growth": 0.05,
                "monthly_savings_rate": 0.2,
                "average_balance": 150000.0,
                "minimum_balance": 50000.0
            },
            "officer_status": officer_status,
            "applied_at": custom_biz["applied_at"][:10]
        }

    # Run live scoring inference using Agent 2 model (Default Dataset)
    try:
        scoring = predict_business(business_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Business {business_id} not found")
    
    # Read profile & timeline metadata
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
def copilot_query(req: CopilotRequest):
    # Retrieve scoring details to use as grounding context
    custom_biz = get_custom_business_detail(req.business_id)
    if custom_biz:
        report_dict = json.loads(custom_biz["data_json"])
        scoring = {
            "score": int(custom_biz["score"]),
            "band": custom_biz["band"],
            "factors": [
                {"name": "GST_Regularity_Score", "label": "GST Regularity", "direction": "+", "weight": 0.4, "detail": "Perfect 12/12 GST filings verified."},
                {"name": "Cash_Buffer_Days", "label": "Cash Buffer", "direction": "+", "weight": 0.3, "detail": "Cash buffer covers 15 days."},
                {"name": "Bounce_Count", "label": "Bounce Count", "direction": "-", "weight": 0.3, "detail": "Zero cheque bounces."}
            ]
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

@app.post("/api/decision")
def save_decision(req: DecisionRequest):
    if req.status not in ALLOWED_DECISION_STATUSES:
        raise HTTPException(status_code=422, detail=f"Invalid status '{req.status}'. Allowed: {sorted(ALLOWED_DECISION_STATUSES)}")
    conn = get_db_connection()
    cursor = conn.cursor()
    ts = datetime.now(timezone.utc).isoformat()
    cursor.execute(
        "INSERT OR REPLACE INTO officer_decisions VALUES (?, ?, ?, ?)",
        (req.business_id, req.status, req.remarks, ts)
    )
    conn.commit()
    conn.close()
    
    add_audit_event("decision", req.business_id, "MSME Business", f"Decision saved: {req.status}. Remarks: {req.remarks}")
    return {"status": "success"}

@app.get("/api/audit")
def get_audit_trail():
    return get_audit_events()


