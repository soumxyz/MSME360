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
        
        # Extract details dynamically from saved JSON data
        avg_revenue = 500000.0
        annual_turnover = 6000000.0
        try:
            data = json.loads(c["data_json"])
            trends = data.get("trends", [])
            if trends:
                avg_revenue = sum(t["revenue"] for t in trends) / len(trends)
            annual_turnover = data.get("gst_analysis", {}).get("annual_turnover", avg_revenue * 12)
        except Exception:
            pass
            
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
        
        # Convert report to JSON-serializable dictionary
        from fastapi.encoders import jsonable_encoder
        report_dict = jsonable_encoder(report)

        # Extract business parameters for persistence
        business_id = msme_input.gstin
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
            
        # Map month trends (mock trends based on actual averages, or real if saved)
        trends = report_dict.get("trends", [])
        if not trends:
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            for idx, m in enumerate(months):
                trends.append({
                    "month": f"2025-{idx+1:02d}",
                    "revenue": 500000 + (idx % 3) * 50000,
                    "expense": 400000 + (idx % 2) * 20000
                })
                
        # Determine average monthly revenue from trends
        avg_revenue = 500000.0
        if trends:
            avg_revenue = sum(t["revenue"] for t in trends) / len(trends)
            
        annual_turnover = report_dict.get("gst_analysis", {}).get("annual_turnover", avg_revenue * 12)
        
        metrics = report_dict.get("metrics", {})
        
        # Get dynamic profile details
        profile = get_dynamic_profile(business_id, custom_biz["name"], annual_turnover, avg_revenue, score)
        
        return {
            "business_id": business_id,
            "profile": {
                "name": custom_biz["name"],
                "owner": profile["owner"],
                "industry": custom_biz["industry"],
                "city": profile["city"],
                "state": profile["state"],
                "business_age_years": profile["business_age_years"],
                "employee_count": profile["employee_count"],
                "category": profile["category"],
                "gst_registered": True,
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


