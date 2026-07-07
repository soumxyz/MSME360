from fastapi.testclient import TestClient
from main import app
import os

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_portfolio():
    response = client.get("/api/portfolio")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "business_id" in data[0]
    assert "score" in data[0]
    assert "officer_status" in data[0]

def test_intake():
    # Test uploading a minimal mock bank statement CSV
    csv_data = b"Date,Credit,Debit,Running_Balance\n2025-07-01,1000,0,1000\n2025-07-15,0,200,800\n2026-02-01,500,0,1300\n"
    files = {
        "bank_file": ("test_bank.csv", csv_data, "text/csv")
    }
    response = client.post("/api/intake", files=files)
    assert response.status_code == 200
    res_json = response.json()
    assert "verdict" in res_json
    assert "checks" in res_json
    # Coverage >= 6 months -> Pass coverage check
    # Bounces/volume low -> Verdict could be YELLOW (low credits)
    assert res_json["verdict"] in ["GREEN", "YELLOW", "RED"]

def test_business_detail():
    response = client.get("/api/business/MSME001")
    assert response.status_code == 200
    data = response.json()
    assert data["business_id"] == "MSME001"
    assert "score" in data["score"]
    assert "factors" in data
    assert len(data["factors"]) == 5

def test_copilot():
    payload = {
        "business_id": "MSME001",
        "message": "Why is the score?"
    }
    response = client.post("/api/copilot", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["answer"]) > 0

def test_intake_register():
    payload = {
        "business_name": "Test Cotton Mills",
        "owner_name": "Vikram Seth",
        "mobile_number": "9999999999",
        "email": "vikram@cotton.com",
        "pan_number": "ABCDE1234F",
        "gstin": "27ABCDE1234F1Z5",
        "udyam_number": "UDYAM-GJ-01-12345",
        "business_type": "Partnership",
        "industry": "Manufacturing",
        "years_in_business": 4,
        "loan_amount_required": 1000000.0,
        "loan_purpose": "Working Capital",
        "connect_gst": True,
        "connect_aa": True,
        "connect_upi": True,
        "connect_epfo": True
    }
    response = client.post("/api/intake/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "business_id" in data
    assert data["score"] > 0
    assert "band" in data
    assert "report" in data


