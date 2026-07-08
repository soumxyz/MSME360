"""
CreditPilot orchestrator tests — real assertions against real code.

These tests exercise the orchestrator's synthesis logic and the /api/creditpilot/*
endpoints without touching the network. The previous version of this file
`print()`ed canned JSON and asserted nothing, which meant a broken orchestrator
still reported green in CI.
"""

from __future__ import annotations

import os
import tempfile
from datetime import date, datetime
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def _isolated_db(monkeypatch):
    """Point db.DB_PATH at a fresh temp SQLite for every test.

    Prevents `test_backend.py`-style pollution of the developer's real
    `msme_workspace.db` and makes runs deterministic.
    """
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    monkeypatch.setenv("MSME_DB_PATH", tmp.name)
    import db as db_mod
    monkeypatch.setattr(db_mod, "DB_PATH", tmp.name)
    import auth as auth_mod
    monkeypatch.setattr(auth_mod, "DB_PATH", tmp.name)
    db_mod.init_db()
    auth_mod.init_auth_tables()
    yield
    try:
        os.unlink(tmp.name)
    except OSError:
        pass


def _officer_headers(client):
    r = client.post("/api/auth/login", json={"username": "officer_demo", "password": "officer123"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


# ---------------------------------------------------------------------------
# _calculate_loan_amount — the P0 bug that hardcoded ₹6L revenue.
# ---------------------------------------------------------------------------

def test_calculate_loan_amount_derives_from_gst_monthly_revenue():
    from creditpilot_orchestrator import CreditPilotOrchestrator

    orch = CreditPilotOrchestrator()
    risk = {"full_report": {}}
    msme = {
        "gst_data": {
            "monthly_revenue": [500_000, 500_000, 500_000],
            "annual_turnover": 6_000_000,
        }
    }
    # score 80 → base = 500_000 * 3 = 1_500_000, * 0.8 = 1_200_000
    amount = orch._calculate_loan_amount(risk, score=80, msme_input_data=msme)
    assert amount == pytest.approx(1_200_000, rel=0.01), (
        f"loan amount should scale with real monthly revenue, got {amount}"
    )


def test_calculate_loan_amount_falls_back_to_annual_turnover():
    from creditpilot_orchestrator import CreditPilotOrchestrator

    orch = CreditPilotOrchestrator()
    msme = {"gst_data": {"annual_turnover": 12_000_000}}  # ₹1L/month
    amount = orch._calculate_loan_amount({"full_report": {}}, score=50, msme_input_data=msme)
    # 1_000_000 * 3 * 0.5 = 1_500_000
    assert amount == pytest.approx(1_500_000, rel=0.01)


def test_calculate_loan_amount_uses_aa_inflows_when_no_gst():
    from creditpilot_orchestrator import CreditPilotOrchestrator

    orch = CreditPilotOrchestrator()
    msme = {"account_aggregator_data": {"monthly_inflows": [800_000, 800_000, 800_000]}}
    amount = orch._calculate_loan_amount({"full_report": {}}, score=100, msme_input_data=msme)
    # 800_000 * 3 * 1.0 = 2_400_000, capped at 2_000_000
    assert amount == 2_000_000


def test_calculate_loan_amount_returns_zero_without_any_signal():
    """
    Previously returned ~₹18L against a hardcoded ₹6L constant — presented as
    "AI-derived". Now returns 0 to force the caller to acknowledge missing data.
    """
    from creditpilot_orchestrator import CreditPilotOrchestrator

    orch = CreditPilotOrchestrator()
    amount = orch._calculate_loan_amount({"full_report": {}}, score=90, msme_input_data={})
    assert amount == 0.0


def test_calculate_loan_amount_capped_at_20_lakh():
    from creditpilot_orchestrator import CreditPilotOrchestrator

    orch = CreditPilotOrchestrator()
    msme = {"gst_data": {"monthly_revenue": [5_000_000] * 12}}  # ₹50L/month
    amount = orch._calculate_loan_amount({"full_report": {}}, score=100, msme_input_data=msme)
    assert amount == 2_000_000, "loan cap should be ₹20L"


# ---------------------------------------------------------------------------
# API-level: /api/creditpilot/status and /api/creditpilot/chat
# ---------------------------------------------------------------------------

def test_creditpilot_status_missing_business():
    from fastapi.testclient import TestClient
    from main import app

    client = TestClient(app)
    r = client.get("/api/creditpilot/status/NOT_A_REAL_ID_1234", headers=_officer_headers(client))
    assert r.status_code in (200, 404), r.text
    if r.status_code == 200:
        body = r.json()
        assert body.get("analyzed") is False or "not analyzed" in str(body).lower()


def test_creditpilot_chat_rejects_unauthenticated():
    from fastapi.testclient import TestClient
    from main import app

    client = TestClient(app)
    r = client.post("/api/creditpilot/chat", json={})
    assert r.status_code == 401, r.text


def test_creditpilot_chat_requires_valid_payload():
    from fastapi.testclient import TestClient
    from main import app

    client = TestClient(app)
    # Missing required fields → 4xx (Pydantic validation), not 500.
    r = client.post("/api/creditpilot/chat", json={}, headers=_officer_headers(client))
    assert 400 <= r.status_code < 500, (
        f"empty body should be a client error, got {r.status_code}: {r.text}"
    )


# ---------------------------------------------------------------------------
# _synthesize_analysis reject path
# ---------------------------------------------------------------------------

def test_synthesize_analysis_rejects_on_red_financial():
    from creditpilot_orchestrator import CreditPilotOrchestrator

    orch = CreditPilotOrchestrator()
    fin = {"status": "RED", "findings": ["Bad data"]}
    risk = {
        "score": 90,
        "risk_category": "Low",
        "confidence": 0.95,
        "findings": [],
        "full_report": {},
    }
    summary, rec, _ = orch._synthesize_analysis(fin, risk, "MSME001", msme_input_data={})
    assert summary["decision"] == "REJECT"
    assert rec["action"] == "REJECT"
    assert rec["recommended_loan"] == 0


def test_synthesize_analysis_conditional_bucket_reduced_amount():
    from creditpilot_orchestrator import CreditPilotOrchestrator

    orch = CreditPilotOrchestrator()
    fin = {"status": "GREEN", "findings": []}
    risk = {
        "score": 60,  # 55..74 → CONDITIONAL_APPROVAL
        "risk_category": "Medium",
        "confidence": 0.80,
        "findings": [],
        "full_report": {},
    }
    msme = {"gst_data": {"monthly_revenue": [500_000] * 6}}
    summary, rec, _ = orch._synthesize_analysis(fin, risk, "MSME002", msme_input_data=msme)
    assert summary["decision"] == "CONDITIONAL_APPROVAL"
    # 500_000 * 3 * 0.6 * 0.8 (conditional discount) = 720_000
    assert rec["recommended_loan"] == pytest.approx(720_000, rel=0.02)
