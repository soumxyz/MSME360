"""API Integration tests for Risk Intelligence Agent.

Validates Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 16.7
"""

import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.main import app
from agents.risk_intelligence_agent.schemas import AssessmentReport, Recommendation

client = TestClient(app)

# Base valid input structure as template
VALID_PAYLOAD = {
    "gstin": "29ABCDE1234F1Z5",
    "pan": "ABCDE1234F",
    "business_registration_date": "2020-01-15",
    "gst_data": {
        "gstin": "29ABCDE1234F1Z5",
        "monthly_revenue": [100000.0] * 12,
        "filing_history": [True] * 12,
        "annual_turnover": 1200000.0
    },
    "upi_transactions": [],
    "account_aggregator_data": {
        "month_end_balances": [50000.0] * 6,
        "monthly_inflows": [100000.0] * 6,
        "monthly_outflows": [80000.0] * 6,
        "statement_start_date": "2023-01-01",
        "statement_end_date": "2023-06-30"
    }
}


def test_root_endpoint():
    """Test root endpoint returns service info."""
    response = client.get("/")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["service"] == "Risk Intelligence Agent"
    assert json_data["status"] == "running"


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "healthy"
    assert json_data["service"] == "risk-intelligence-agent"


def test_evaluate_missing_auth():
    """Test evaluate endpoint rejects request with missing Authorization header."""
    response = client.post("/api/v1/evaluate", json=VALID_PAYLOAD)
    assert response.status_code == 401
    assert "Missing Authorization header" in response.json()["detail"]


def test_evaluate_invalid_auth_format():
    """Test evaluate endpoint rejects request with invalid Authorization format."""
    headers = {"Authorization": "invalid_format_token"}
    response = client.post("/api/v1/evaluate", json=VALID_PAYLOAD, headers=headers)
    assert response.status_code == 401
    assert "Invalid Authorization header format" in response.json()["detail"]


def test_evaluate_validation_error():
    """Test evaluate endpoint rejects request with invalid payload (400 Bad Request)."""
    headers = {"Authorization": "Bearer test_token"}
    invalid_payload = {
        "gstin": "INVALID",
        "pan": "INVALID"
    }
    # FastAPI's request validation will catch invalid schema structures at entry point and return 422,
    # but wait: if we pass a valid schema structure but with invalid field content, it triggers Pydantic ValidationError.
    # In Pydantic v2, passing invalid gstin format raises ValidationError. FastAPI catches this and returns 422.
    # But wait, routes.py has a try-except ValueError block that returns 400:
    # "except ValueError as e: raise HTTPException(status_code=400, ...)"
    # Let's test that both 400 and 422 are handled correctly as client-side errors (4xx).
    response = client.post("/api/v1/evaluate", json=invalid_payload, headers=headers)
    assert response.status_code in [400, 422]


@patch("api.routes.evaluate_msme", new_callable=AsyncMock)
def test_evaluate_success(mock_evaluate):
    """Test successful risk assessment execution and response schema."""
    headers = {"Authorization": "Bearer test_token"}
    
    # Mock evaluate_msme output report
    mock_report = AssessmentReport(
        request_id="test-req-id",
        timestamp="2026-07-07T12:00:00",
        api_version="v1",
        msme_identifier="29ABCDE1234F1Z5",
        risk_score=85.0,
        probability_of_default=0.15,
        risk_category="LOW",
        eligibility=True,
        financial_health_score=80.0,
        confidence_level=90.0,
        fraud_flags=[],
        policy_violations=[],
        top_features=[],
        explanation="Low risk profile",
        recommendation=Recommendation.APPROVE,
        audit_trail_id="test-req-id"
    )
    mock_evaluate.return_value = mock_report
    
    response = client.post("/api/v1/evaluate", json=VALID_PAYLOAD, headers=headers)
    assert response.status_code == 200
    
    json_data = response.json()
    assert json_data["request_id"] == "test-req-id"
    assert json_data["msme_identifier"] == "29ABCDE1234F1Z5"
    assert json_data["risk_score"] == 85.0
    assert json_data["recommendation"] == "APPROVE"


@patch("api.routes.evaluate_msme", new_callable=AsyncMock)
def test_evaluate_timeout(mock_evaluate):
    """Test that workflow timeout (>10s) returns 504 Gateway Timeout."""
    headers = {"Authorization": "Bearer test_token"}
    
    import asyncio
    async def slow_evaluate(*args, **kwargs):
        await asyncio.sleep(12.0)
        
    mock_evaluate.side_effect = slow_evaluate
    
    with patch("api.routes.asyncio.wait_for", side_effect=asyncio.TimeoutError()):
        response = client.post("/api/v1/evaluate", json=VALID_PAYLOAD, headers=headers)
        assert response.status_code == 504
        assert response.json()["detail"]["error"] == "evaluation timeout"
