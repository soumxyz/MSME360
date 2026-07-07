# Frontend API Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Connect the React frontend pages and state handlers to the live FastAPI backend server (`http://localhost:8000/api`) to enable live document uploads, dynamic XGBoost scoring, active Gemini Copilot chats, and SQLite audit trail replication.

**Architecture:** Update the frontend API layer (`frontend/src/lib/api/index.ts`) to communicate with uvicorn via `fetch` calls, and hook react-query and event triggers in the intake, detail, copilot, and audit pages to load and post data dynamically.

**Tech Stack:** React, TypeScript, TanStack Query (React Query)

## Global Constraints
- Backend API base: `http://localhost:8000/api`.
- Form data uploads use multipart encoding.
- Response payloads must maintain current TypeScript shape boundaries in `types.ts`.

---

### Task 1: Implement Fetch-based API Layer

**Files:**
- Modify: `frontend/src/lib/api/index.ts`
- Modify: `frontend/src/lib/api/hooks.ts`

**Interfaces:**
- Consumes: Backend uvicorn server running on `http://localhost:8000/api`.
- Produces: TypeScript promises returning `PortfolioRow[]`, `BusinessDetail`, `AuditEvent[]`, and chat responses.

- [ ] **Step 1: Update API index.ts with fetch requests**
  Replace [index.ts](file:///d:/idbi-proj/frontend/src/lib/api/index.ts) with direct network calls:
  ```typescript
  import type { BusinessDetail, PortfolioRow } from "./types";
  import type { AuditEvent } from "../audit";

  const BASE_URL = "http://localhost:8000/api";

  export async function getPortfolio(): Promise<PortfolioRow[]> {
    const res = await fetch(`${BASE_URL}/portfolio`);
    if (!res.ok) throw new Error("Failed to fetch portfolio");
    return res.json();
  }

  export async function getBusinessDetail(id: string): Promise<BusinessDetail> {
    const res = await fetch(`${BASE_URL}/business/${id}`);
    if (!res.ok) throw new Error(`Failed to fetch detail for business ${id}`);
    return res.json();
  }

  export async function submitIntake(bankFile: File, gstFile?: File): Promise<{ verdict: "GREEN" | "YELLOW" | "RED"; checks: any[] }> {
    const formData = new FormData();
    formData.append("bank_file", bankFile);
    if (gstFile) {
      formData.append("gst_file", gstFile);
    }
    const res = await fetch(`${BASE_URL}/intake`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error("Intake submission failed");
    return res.json();
  }

  export async function submitDecision(businessId: string, status: string, remarks: string): Promise<void> {
    const res = await fetch(`${BASE_URL}/decision`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ business_id: businessId, status, remarks }),
    });
    if (!res.ok) throw new Error("Decision submission failed");
  }

  export async function queryCopilot(businessId: string, message: string): Promise<{ answer: string }> {
    const res = await fetch(`${BASE_URL}/copilot`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ business_id: businessId, message }),
    });
    if (!res.ok) throw new Error("Copilot query failed");
    return res.json();
  }

  export async function getAuditTrail(): Promise<AuditEvent[]> {
    const res = await fetch(`${BASE_URL}/audit`);
    if (!res.ok) throw new Error("Failed to fetch audit log");
    return res.json();
  }
  ```

- [ ] **Step 2: Add Audit Log query hook**
  Modify [hooks.ts](file:///d:/idbi-proj/frontend/src/lib/api/hooks.ts) to add an audit trail hook:
  ```typescript
  import { useQuery } from "@tanstack/react-query";
  import { getBusinessDetail, getPortfolio, getAuditTrail } from "./index";

  export function usePortfolio() {
    return useQuery({ queryKey: ["portfolio"], queryFn: getPortfolio });
  }

  export function useBusinessDetail(id: string | undefined) {
    return useQuery({
      queryKey: ["business", id],
      queryFn: () => getBusinessDetail(id!),
      enabled: !!id,
    });
  }

  export function useAuditTrail() {
    return useQuery({
      queryKey: ["audit-trail"],
      queryFn: getAuditTrail,
      refetchInterval: 5000, // Auto-refresh audit trail every 5 seconds
    });
  }
  ```

---

### Task 2: Integrate Intake and Manual Decision Screens

**Files:**
- Modify: `frontend/src/pages/NewApplication.tsx:50-80` (Verify logic handles file upload state)
- Modify: `frontend/src/pages/BusinessDetail.tsx:140-190` (Verify decision bar callback updates status)

**Interfaces:**
- Consumes: `submitIntake` and `submitDecision` async functions.
- Produces: Interactive uploads updating route views.

- [ ] **Step 1: Integrate Intake file uploads**
  Modify [NewApplication.tsx](file:///d:/idbi-proj/frontend/src/pages/NewApplication.tsx). Replace the mock `setTimeout` simulation in `onDrop` with a real API call:
  ```typescript
  // Replace the mock handler in NewApplication.tsx
  const handleFileUpload = async (bankFile: File, gstFile?: File) => {
    setIsScanning(true);
    setError(null);
    try {
      const result = await submitIntake(bankFile, gstFile);
      setVerdict(result.verdict);
      setChecks(result.checks);
    } catch (e: any) {
      setError(e.message || "Failed to process files");
    } finally {
      setIsScanning(false);
    }
  };
  ```

- [ ] **Step 2: Integrate decision sticky bar**
  Modify [BusinessDetail.tsx](file:///d:/idbi-proj/frontend/src/pages/BusinessDetail.tsx). Locate the decision submit callback and invoke the database sync function:
  ```typescript
  // Update decision submit handler in BusinessDetail.tsx
  const handleDecisionSave = async (status: string, remarks: string) => {
    try {
      await submitDecision(businessId, status, remarks);
      // Invalidate queries to reload detail state
      queryClient.invalidateQueries({ queryKey: ["business", businessId] });
      queryClient.invalidateQueries({ queryKey: ["portfolio"] });
    } catch (e: any) {
      console.error("Failed to save decision", e);
    }
  };
  ```

---

### Task 3: Integrate Copilot Drawer and Audit Log Views

**Files:**
- Modify: `frontend/src/components/ChatPanel.tsx:65-90`
- Modify: `frontend/src/pages/AuditLog.tsx:40-70`

**Interfaces:**
- Consumes: `queryCopilot` and `useAuditTrail` hooks.
- Produces: Live LLM chat bubbles and database logs listing.

- [ ] **Step 1: Integrate Copilot drawer**
  Modify [ChatPanel.tsx](file:///d:/idbi-proj/frontend/src/components/ChatPanel.tsx). Replace the mock response timer with a real backend call:
  ```typescript
  // Replace the mock copilot handler in ChatPanel.tsx
  const handleSend = async (text: string) => {
    const userMsg = { id: `msg-${Date.now()}`, sender: "user" as const, content: text };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);
    try {
      const response = await queryCopilot(business.business_id, text);
      const copilotMsg = { id: `msg-${Date.now()}`, sender: "copilot" as const, content: response.answer };
      setMessages((prev) => [...prev, copilotMsg]);
    } catch (e: any) {
      const errMsg = { id: `msg-${Date.now()}`, sender: "copilot" as const, content: "Error: Failed to connect to copilot server." };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setIsLoading(false);
    }
  };
  ```

- [ ] **Step 2: Integrate Audit Log**
  Modify [AuditLog.tsx](file:///d:/idbi-proj/frontend/src/pages/AuditLog.tsx). Swap the local array/localStorage read with our React Query `useAuditTrail()` hook:
  ```typescript
  // Replace the local state loading in AuditLog.tsx
  const { data: auditEvents = [], isLoading } = useAuditTrail();
  ```
