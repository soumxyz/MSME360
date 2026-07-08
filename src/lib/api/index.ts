import type { BusinessDetail, PortfolioRow } from "./types";
import type { AuthState, Role } from "../auth";
import { clearAuth, getAuthHeaders, setAuth } from "../auth";
import type { AuditEvent } from "../audit";

// Prefer VITE_API_URL from the env; fall back to localhost so `npm run dev`
// works out of the box. `import.meta.env` is inlined at build time by Vite,
// so a real deploy sets VITE_API_URL to the production API origin.
const BASE_URL: string =
  (import.meta.env.VITE_API_URL as string | undefined) ?? "http://localhost:8000/api";

/**
 * Fetch wrapper that automatically:
 *   - attaches the Bearer token from lib/auth
 *   - JSON-encodes the body if `json` is passed
 *   - clears local auth on a 401 so ProtectedRoute redirects to /login
 *   - throws an Error carrying the parsed message
 */
async function apiFetch<T>(
  path: string,
  opts: {
    method?: "GET" | "POST" | "PUT" | "DELETE";
    json?: unknown;
    body?: BodyInit;
    headers?: Record<string, string>;
  } = {}
): Promise<T> {
  const headers: Record<string, string> = {
    ...getAuthHeaders(),
    ...(opts.headers ?? {}),
  };
  let body: BodyInit | undefined = opts.body;
  if (opts.json !== undefined) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(opts.json);
  }
  const res = await fetch(`${BASE_URL}${path}`, {
    method: opts.method ?? "GET",
    headers,
    body,
  });
  if (res.status === 401) {
    // Token expired or missing → drop it so the app kicks the user to /login.
    clearAuth();
  }
  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    throw new Error(txt || `Request failed with status ${res.status}`);
  }
  // 204/no-content
  if (res.status === 204) return undefined as T;
  const ct = res.headers.get("content-type") ?? "";
  if (ct.includes("application/json")) {
    return (await res.json()) as T;
  }
  return (await res.text()) as unknown as T;
}

// -------- Auth --------
export interface LoginResponse {
  access_token: string;
  token_type: "bearer";
  role: Role;
  username: string;
  expires_at: string;
}

export async function login(username: string, password: string): Promise<AuthState> {
  const res = await apiFetch<LoginResponse>("/auth/login", {
    method: "POST",
    json: { username, password },
  });
  const state: AuthState = {
    token: res.access_token,
    role: res.role,
    username: res.username,
    expiresAt: res.expires_at,
  };
  setAuth(state);
  return state;
}

export async function me(): Promise<{ username: string; role: Role }> {
  return apiFetch("/auth/me");
}

export function logout(): void {
  clearAuth();
}

// -------- Portfolio & business --------
export async function getPortfolio(): Promise<PortfolioRow[]> {
  return apiFetch<PortfolioRow[]>("/portfolio");
}

export async function getBusinessDetail(id: string): Promise<BusinessDetail> {
  return apiFetch<BusinessDetail>(`/business/${id}`);
}

// -------- Intake (open — customer-facing signup path) --------
export interface IntakeChecksResult {
  verdict: "GREEN" | "YELLOW" | "RED";
  checks: Array<Record<string, unknown>>;
}

export async function submitIntake(bankFile: File, gstFile?: File): Promise<IntakeChecksResult> {
  const formData = new FormData();
  formData.append("bank_file", bankFile);
  if (gstFile) formData.append("gst_file", gstFile);
  return apiFetch<IntakeChecksResult>("/intake", { method: "POST", body: formData });
}

// -------- Officer decisions --------
export async function submitDecision(businessId: string, status: string, remarks: string): Promise<void> {
  await apiFetch<void>("/decision", {
    method: "POST",
    json: { business_id: businessId, status, remarks },
  });
}

// -------- Copilot chat --------
export async function queryCopilot(businessId: string, message: string): Promise<{ answer: string }> {
  return apiFetch("/copilot", {
    method: "POST",
    json: { business_id: businessId, message },
  });
}

// -------- Audit trail --------
export async function getAuditTrail(): Promise<AuditEvent[]> {
  return apiFetch<AuditEvent[]>("/audit");
}

// -------- MSME registration payload --------
export interface RegisterMSMEPayload {
  business_name: string;
  owner_name: string;
  mobile_number: string;
  email: string;
  pan_number: string;
  gstin?: string;
  udyam_number?: string;
  business_type: string;
  industry: string;
  years_in_business: number;
  loan_amount_required: number;
  loan_purpose: string;
  connect_gst?: boolean;
  connect_aa?: boolean;
  connect_upi?: boolean;
  connect_epfo?: boolean;
  upload_pan?: string;
  upload_aadhaar?: string;
  upload_udyam?: string;
  upload_bank?: string;
}

export interface RegisterMSMEResponse {
  business_id: string;
  score: number;
  band: string;
  report: Record<string, unknown>;
  data_provenance?: {
    gst: "connected" | "uploaded" | "estimated";
    aa: "connected" | "uploaded" | "estimated";
    upi: "connected" | "uploaded" | "estimated";
    epfo: "connected" | "uploaded" | "estimated";
  };
}

export async function registerMSME(payload: RegisterMSMEPayload): Promise<RegisterMSMEResponse> {
  return apiFetch<RegisterMSMEResponse>("/intake/register", { method: "POST", json: payload });
}

// -------- OCR --------
export interface OcrExtractResult {
  success: boolean;
  source: "csv_parser" | "gemini_vision" | "mock_fallback";
  extracted: {
    business_name?: string | null;
    owner_name?: string | null;
    account_number?: string | null;
    ifsc_code?: string | null;
    bank_name?: string | null;
    pan_number?: string | null;
    gstin?: string | null;
    statement_period_start?: string | null;
    statement_period_end?: string | null;
    total_credits?: number | null;
    total_debits?: number | null;
    closing_balance?: number | null;
    average_balance?: number | null;
    transaction_count?: number | null;
    industry_hint?: string | null;
    _mock?: boolean;
    _note?: string;
  };
  _error?: string;
}

export async function extractDocument(file: File): Promise<OcrExtractResult> {
  const formData = new FormData();
  formData.append("file", file);
  return apiFetch<OcrExtractResult>("/ocr/extract", { method: "POST", body: formData });
}
