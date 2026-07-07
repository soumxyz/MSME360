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
