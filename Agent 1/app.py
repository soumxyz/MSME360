from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn

from agents.agent_one import verify_files

app = FastAPI(
    title="CreditPulse AI — Backend Services",
    description="Backend API supporting Intake Verification (Agent 1) and downstream scoring/chat services.",
    version="1.0.0"
)

# Enable CORS for React frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify front-end origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "status": "online",
        "agent": "Agent 1 — Intake & Verification Server"
    }


@app.post("/verify")
async def verify_upload(
    bank_statement: UploadFile = File(..., description="Uploaded Bank Statement CSV"),
    gst_summary: Optional[UploadFile] = File(None, description="Uploaded GST Summary CSV (optional)")
):
    """
    FastAPI Endpoint for Agent 1.
    Accepts CSV bank statement and optional GST summary files, runs intake verification checks,
    and returns a readiness report with detail logs.
    """
    # 1. Read Bank Statement
    if not bank_statement.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Bank statement must be a CSV file.")
    
    try:
        bank_bytes = await bank_statement.read()
        bank_csv_content = bank_bytes.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read bank statement file: {str(e)}")

    # 2. Read GST Summary (if provided)
    gst_csv_content = None
    if gst_summary:
        if not gst_summary.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="GST summary must be a CSV file.")
        
        try:
            gst_bytes = await gst_summary.read()
            gst_csv_content = gst_bytes.decode("utf-8")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read GST summary file: {str(e)}")

    # 3. Call Agent 1 Validation Logic
    try:
        report = verify_files(bank_csv_content, gst_csv_content)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal verification error: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
