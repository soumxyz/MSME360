"""
Backend endpoint tests. Each test runs against an isolated temp SQLite so runs
do not pollute the developer's real msme_workspace.db.
"""

from __future__ import annotations

import os
import tempfile

import pytest


@pytest.fixture(autouse=True)
def _isolated_db(monkeypatch):
    """Redirect db.DB_PATH to a temp file for each test; drop it after.

    Also seeds the auth tables so the officer_demo / customer_demo login fixtures
    have real bcrypt-hashed rows to authenticate against.
    """
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    import db as db_mod
    monkeypatch.setattr(db_mod, "DB_PATH", tmp.name)
    # `auth.py` captured DB_PATH at import time — override its copy too.
    import auth as auth_mod
    monkeypatch.setattr(auth_mod, "DB_PATH", tmp.name)
    db_mod.init_db()
    auth_mod.init_auth_tables()
    yield
    try:
        os.unlink(tmp.name)
    except OSError:
        pass


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from main import app
    return TestClient(app)


def _login(client, username: str, password: str) -> str:
    r = client.post("/api/auth/login", json={"username": username, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.fixture
def officer_headers(client):
    token = _login(client, "officer_demo", "officer123")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def customer_headers(client):
    token = _login(client, "customer_demo", "customer123")
    return {"Authorization": f"Bearer {token}"}


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_portfolio_requires_auth(client):
    """Officer-only route: unauthenticated request must be 401."""
    r = client.get("/api/portfolio")
    assert r.status_code == 401, r.text


def test_portfolio_forbids_customer(client, customer_headers):
    """Customer role token must not be able to view the officer portfolio."""
    r = client.get("/api/portfolio", headers=customer_headers)
    assert r.status_code == 403, r.text


def test_portfolio_returns_list(client, officer_headers):
    response = client.get("/api/portfolio", headers=officer_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # If dataset seed exists, first row should have the contract fields.
    if data:
        assert "business_id" in data[0]
        assert "score" in data[0]
        assert "officer_status" in data[0]


def test_intake_smoke(client):
    csv_data = (
        b"Date,Credit,Debit,Running_Balance\n"
        b"2025-07-01,1000,0,1000\n"
        b"2025-07-15,0,200,800\n"
        b"2026-02-01,500,0,1300\n"
    )
    files = {"bank_file": ("test_bank.csv", csv_data, "text/csv")}
    response = client.post("/api/intake", files=files)
    assert response.status_code == 200
    body = response.json()
    assert body["verdict"] in ["GREEN", "YELLOW", "RED"]
    assert isinstance(body.get("checks"), list)


@pytest.mark.skipif(
    not os.path.exists(
        os.path.join(os.path.dirname(__file__), "..", "Dataset", "features.csv")
    ),
    reason="Requires seeded Dataset/features.csv",
)
def test_business_detail_seeded(client, officer_headers):
    response = client.get("/api/business/MSME001", headers=officer_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["business_id"] == "MSME001"
    assert isinstance(data["factors"], list)


def test_business_detail_unknown_id_is_404(client, officer_headers):
    """
    Previously fell through to `iloc[0]` on an empty DataFrame → IndexError → 500.
    It should return a clean 404 for an unknown id.
    """
    response = client.get(
        "/api/business/DEFINITELY_NOT_A_REAL_ID_9999", headers=officer_headers
    )
    assert response.status_code == 404, response.text


def test_intake_register_rejects_invalid_pan(client):
    """
    Previously silently substituted "ABCDE1234F" into the audit trail.
    Must now 400 the request.
    """
    payload = {
        "business_name": "Bad PAN Co.",
        "owner_name": "T. Est",
        "mobile_number": "9999999999",
        "email": "t@example.com",
        "pan_number": "GARBAGE",
        "business_type": "Sole Proprietor",
        "industry": "Retail",
        "years_in_business": 3,
        "loan_amount_required": 500_000.0,
        "loan_purpose": "Working Capital",
    }
    response = client.post("/api/intake/register", json=payload)
    assert response.status_code == 400, response.text
    assert "PAN" in response.text


def test_decision_endpoint_requires_officer(client, customer_headers):
    """Customer role cannot approve loans."""
    r = client.post(
        "/api/decision",
        json={"business_id": "MSME001", "status": "Approved", "remarks": "x"},
        headers=customer_headers,
    )
    assert r.status_code == 403, r.text


def test_decision_endpoint_writes_and_appears_in_audit(client, officer_headers):
    """
    /api/decision must:
      1. Reject an unknown business_id with 404 (no orphan writes).
      2. Persist decisions for a known business.
      3. Surface the decision in the audit trail.
    """
    unknown = client.post(
        "/api/decision",
        json={"business_id": "NO_SUCH_ID", "status": "Approved", "remarks": "x"},
        headers=officer_headers,
    )
    assert unknown.status_code == 404, unknown.text

    reg = client.post(
        "/api/intake/register",
        json={
            "business_name": "Audit Test Weaves",
            "owner_name": "A. Uditor",
            "mobile_number": "9000000000",
            "email": "a@example.com",
            "pan_number": "ABCDE1234F",
            "gstin": "27ABCDE1234F1Z5",
            "business_type": "Partnership",
            "industry": "Manufacturing",
            "years_in_business": 5,
            "loan_amount_required": 1_000_000.0,
            "loan_purpose": "Machinery",
            "connect_gst": True,
        },
    )
    assert reg.status_code == 200, reg.text
    business_id = reg.json()["business_id"]

    decision = client.post(
        "/api/decision",
        json={"business_id": business_id, "status": "Approved", "remarks": "Clean file"},
        headers=officer_headers,
    )
    assert decision.status_code == 200, decision.text

    audit = client.get("/api/audit", headers=officer_headers)
    assert audit.status_code == 200
    events = audit.json()
    assert any(
        e.get("business_id") == business_id and "Approved" in e.get("summary", "")
        for e in events
    ), "decision should appear in audit events"


def test_copilot_requires_auth(client):
    """Copilot must reject unauthenticated calls."""
    r = client.post("/api/copilot", json={"business_id": "MSME001", "message": "hi"})
    assert r.status_code == 401, r.text


def test_copilot_returns_answer_string(client, officer_headers):
    """
    Copilot should never 500 on a well-formed request even if no LLM key is set —
    it falls back to a templated response.
    """
    response = client.post(
        "/api/copilot",
        json={"business_id": "MSME001", "message": "Why is the score low?"},
        headers=officer_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data.get("answer"), str)
    assert len(data["answer"]) > 0


def test_login_rejects_bad_password(client):
    r = client.post("/api/auth/login", json={"username": "officer_demo", "password": "wrong"})
    assert r.status_code == 401


def test_me_returns_role(client, officer_headers):
    r = client.get("/api/auth/me", headers=officer_headers)
    assert r.status_code == 200
    assert r.json() == {"username": "officer_demo", "role": "officer"}


def test_intake_register_provenance_marks_uncosnnected_sources_as_estimated(client):
    payload = {
        "business_name": "No Consent Traders",
        "owner_name": "Off Grid",
        "mobile_number": "9999999999",
        "email": "og@example.com",
        "pan_number": "ABCDE1234F",
        "business_type": "Partnership",
        "industry": "Retail",
        "years_in_business": 2,
        "loan_amount_required": 500_000.0,
        "loan_purpose": "Working Capital",
        # No connect_* flags set.
    }
    response = client.post("/api/intake/register", json=payload)
    assert response.status_code == 200, response.text
    body = response.json()
    provenance = body["data_provenance"]
    assert provenance["gst"] == "estimated"
    assert provenance["aa"] == "estimated"
    assert provenance["upi"] == "estimated"
    assert provenance["epfo"] == "estimated"
