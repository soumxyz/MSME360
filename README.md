# MSME360 — Alternate-data credit workspace

A React + FastAPI demo platform for small-business (MSME) credit assessment.
Two role-based experiences:

- **Customer** (`/customer/*`) — MSMEs register a business, upload consent-driven
  documents, and view a pre-qualified credit report.
- **Officer** (`/officer/*`) — Bank credit officers review the application queue,
  see the AI-driven risk score with SHAP-style factor attribution, chat with the
  Credit Copilot, and record Approve/Reject/Conditional decisions.

## Stack

| Layer     | Choice                                                         |
|-----------|----------------------------------------------------------------|
| Frontend  | React 19 + TypeScript + Vite + Tailwind + React Router + React Query + Recharts |
| Backend   | FastAPI + SQLite + Pydantic v2 + JWT auth (python-jose + passlib) |
| ML        | XGBoost model + SHAP explanations (see `risk agent/`)          |
| Data      | Seeded CSVs in `Dataset/` for demo; SQLite at `backend/msme_workspace.db` |

## Getting started

### 1. Backend

```bash
cd backend
python -m venv .venv && source .venv/Scripts/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env    # edit JWT_SECRET etc.
python -m uvicorn main:app --reload --port 8000
```

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
