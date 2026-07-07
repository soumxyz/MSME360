# Design Spec — FastAPI Backend & SQLite Audit Log

**Date:** 2026-07-07  
**Status:** Draft (Pending User Review)  
**Author:** AI Coding Assistant  

---

## 1. Objectives & API Alignment
- **Goal**: Implement a FastAPI Python backend serving the MSME Credit Intelligence Workspace.
- **Frontend Contract**: Match the API contract expected by our React frontend (`getPortfolio`, `getBusinessDetail`, `POST /api/intake`, `POST /api/copilot`, `POST /api/decision`, `GET /api/audit`).
- **Database**: Use a SQLite database for compliance logging, and combine it with Python-based CSV reading for business metadata.

---

## 2. API Endpoints Schema
The backend will expose the following endpoints:

### `GET /api/portfolio`
- **Output**: Array of portfolio rows.
- **Logic**: Reads `Dataset/engineered_features.csv` and `Dataset/credit_labels.csv`, joins them, and formats them matching `PortfolioRow` TypeScript interfaces. Looks up decision status from the SQLite database.

### `GET /api/business/{id}`
- **Output**: Complete business detail JSON structure.
- **Logic**: Loads the profile from `Dataset/businesses.csv`, queries the GST timeline from `Dataset/gst_summary.csv`, runs live ML inference using `Dataset/score_inference.py`, and reads the latest decision status from the SQLite database.

### `POST /api/intake`
- **Input**: Multipart form-data uploading two files (`bank_statement`, `gst_summary`).
- **Logic**: Runs Agent 1 validation rules on the files. Returns a Red/Yellow/Green verdict and a list of checklist results.

### `POST /api/copilot`
- **Input**: JSON payload `{ "business_id": "...", "message": "..." }`.
- **Logic**: Resolves the LLM client based on environment variables:
  - If `OPENAI_API_KEY` is set, uses the OpenAI API.
  - If `GEMINI_API_KEY` is set, uses the Gemini API.
  - If no key is set, falls back to a simulated grounded response matching the scored factors.
- **Logs**: Writes the query and answer to the SQLite audit log.

### `GET /api/audit`
- **Output**: Array of audit log events from the SQLite database.

### `POST /api/decision`
- **Input**: JSON payload `{ "business_id": "...", "status": "...", "remarks": "..." }`.
- **Logic**: Writes the final credit decision (Approve/Conditional/Reject) and remarks to the SQLite audit log and updates the local state.

---

## 3. Database Schema (SQLite)
File: `backend/msme_workspace.db`

### Table: `officer_decisions`
- `business_id` (TEXT, Primary Key)
- `status` (TEXT, e.g. "Approved", "Conditional", "Rejected")
- `remarks` (TEXT)
- `updated_at` (TEXT)

### Table: `audit_events`
- `id` (TEXT, Primary Key)
- `ts` (TEXT)
- `type` (TEXT)
- `business_id` (TEXT)
- `business_name` (TEXT)
- `actor` (TEXT)
- `summary` (TEXT)
- `payload` (TEXT, JSON string)

---

## 4. Run Strategy
- **Framework**: `fastapi` and `uvicorn`.
- **CORS**: Configured to allow requests from the React dev server (`http://localhost:5173`).
