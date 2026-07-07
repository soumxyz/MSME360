# Design Spec — Frontend API Integration

**Date:** 2026-07-07  
**Status:** Draft (Pending User Review)  
**Author:** AI Coding Assistant  

---

## 1. Objectives
- Connect the React + Vite frontend directly to the FastAPI server (`http://localhost:8000`) for all actions.
- Replace client-side local simulations and `localStorage` caching with real network requests.
- Enable live intake uploads, real-time ML score rendering, active Gemini Copilot chats, and persistent SQLite compliance logging.

---

## 2. API Layer Mapping
We will update [index.ts](file:///d:/idbi-proj/frontend/src/lib/api/index.ts) to define a central `BASE_URL = "http://localhost:8000/api"` and implement the following async functions:

- **`getPortfolio()`**: `GET /portfolio`
- **`getBusinessDetail(id: string)`**: `GET /business/{id}`
- **`submitIntake(bankFile: File, gstFile?: File)`**: `POST /intake` (multipart/form-data)
- **`submitDecision(businessId: str, status: str, remarks: str)`**: `POST /decision` (JSON payload)
- **`queryCopilot(businessId: str, message: str)`**: `POST /copilot` (JSON payload)
- **`getAuditTrail()`**: `GET /audit`

---

## 3. UI Component Integration
### 1. New application Intake (`NewApplication.tsx`)
- On dropping a file, instead of setting a 1.5s timeout with simulated results, perform a real `FormData` request to `POST /api/intake` using `submitIntake(bankFile, gstFile)`.
- Render the checks list and readiness verdict directly from the backend response.

### 2. Credit Copilot Drawer (`ChatPanel.tsx`)
- When the user sends a message, call `queryCopilot(businessId, message)`.
- Render the text response returned by the backend (which runs the grounded Gemini model).

### 3. Review Decision Sticky Bar (`DecisionBar.tsx` / `BusinessDetail.tsx`)
- When saving an officer decision (Approve / Conditional / Reject / Request info), call `submitDecision(businessId, status, remarks)`.
- Reload details on success.

### 4. Audit Log Viewer (`AuditLog.tsx`)
- Load logs using React Query calling `getAuditTrail()`, updating the table dynamically with persistent database events.
