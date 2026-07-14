# MSME360 — Alternate-data credit workspace

A React + FastAPI demo platform for small-business (MSME) credit assessment.
Two role-based experiences:

- **Customer** (`/customer/*`) — MSMEs register a business, upload consent-driven
  documents, and view a pre-qualified credit report.
- **Officer** (`/officer/*`) — Bank credit officers review the application queue,
  see the AI-driven risk score with SHAP-style factor attribution, chat with the
  Credit Copilot, and record Approve/Reject/Conditional decisions.

## Multi-Agent Architecture (CreditPilot)

The workspace orchestrates three specialized AI agents to evaluate credit applications:

1. **Financial Intelligence Agent (Agent 1)** — *Data Quality & Compliance*
   - Validates CSV file structures and schemas.
   - Checks date coverage (requires at least 6 months of banking history).
   - Recalculates accounting flows to ensure the ledger reconciles with 0% drift.
   - Cross-references bank statement credits against GST sales.
   - Rejects the application early (RED verdict) if critical data anomalies or gaps are detected.

2. **Risk Intelligence Agent (Agent 2)** — *Credit Risk Assessment*
   - Orchestrates a modular machine learning pipeline via a LangGraph state graph.
   - Predicts default probability using an XGBoost model across 8 financial/operational features.
   - Generates SHAP values for localized feature attribution (explaining what raised or lowered the score).
   - Cross-checks applications against business policy rules and fraud heuristics.
   - Employs Google Gemini (or a fallback tree) to translate data into plain-language bullet points.

3. **CreditPilot Copilot (Agent 3)** — *Conversational Synthesis*
   - Synthesizes findings from Agent 1 and Agent 2 to recommend final lending terms (e.g., dynamically calculating a safe loan offer capped at ₹20 Lakhs based on monthly revenue).
   - Powers the interactive panel in the underwriting UI for credit officers to query details (e.g., scenario analysis: *"What if we reduce the loan to ₹15 lakh?"*).

---

## Stack

| Layer     | Choice                                                         |
|-----------|----------------------------------------------------------------|
| Frontend  | React 19 + TypeScript + Vite + Tailwind + React Router + React Query + Recharts |
| Backend   | FastAPI + SQLite + Pydantic v2 + JWT auth (python-jose + passlib) |
| ML        | XGBoost model + SHAP explanations (see `risk agent/`)          |
| Data      | Seeded CSVs in `Dataset/` for demo; SQLite at `backend/msme_workspace.db` |

---

## Getting started

### 1. Backend

```bash
cd backend
python -m venv .venv && source .venv/Scripts/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env    # edit JWT_SECRET and add LLM API keys
python -m uvicorn main:app --reload --port 8000
```

Note: To enable live LLM reasoning and conversational capabilities, add your `GEMINI_API_KEY` (or `GROQ_API_KEY` / `OPENROUTER_API_KEY`) to the `backend/.env` file. If none are provided, the system falls back to a smart mock response engine.

Demo users are seeded on first startup:

| Username        | Password      | Role     |
|-----------------|---------------|----------|
| `officer_demo`  | `officer123`  | officer  |
| `customer_demo` | `customer123` | customer |

Change them via a proper user-provisioning flow before deploying anywhere.

### 2. Frontend

```bash
npm install
cp .env.example .env    # sets VITE_API_URL
npm run dev
```

Open http://localhost:5173/login and sign in with one of the demo accounts above.

### 3. Tests

Backend:

```bash
cd backend
pytest -v
```

Every test runs against an isolated temp SQLite; no test touches your dev DB.

## Layout

```
backend/           FastAPI app (main.py, auth.py, db.py, agent*.py, creditpilot_*.py)
src/               React app
  App.tsx          Router + ProtectedRoute wrappers + ErrorBoundary
  layouts/         CustomerLayout, OfficerLayout
  pages/           17 route components
  components/      ChatPanel, MemoModal, ScoreGauge, FactorBars, Skeleton, ErrorBoundary, ProtectedRoute
  lib/
    api/           Fetch client + react-query hooks + wire types
    auth.ts        Token store (localStorage)
    format.ts      INR / date formatters
    palette.ts     Brand colours
Dataset/           Static features CSV + HANDOFF.md wire contract
risk agent/        Standalone risk intelligence agent (imported via sys.path)
```

## Security posture

Real, server-side auth is enforced. Every officer-only route in `backend/main.py`
uses `Depends(require_officer)`; `<ProtectedRoute>` in `src/App.tsx` is a UX
convenience, **not** the security boundary.

CORS is env-driven (`CORS_ALLOW_ORIGINS`) with `credentials=true`, so any deploy
must set an explicit allowlist — no wildcards.

## Contributing

Before opening a PR:

```bash
npm run lint && npm run build   # frontend
cd backend && pytest -v         # backend
```
