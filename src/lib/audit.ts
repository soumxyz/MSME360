export type AuditEventType = "score" | "copilot" | "decision" | "intake";

export interface AuditEvent {
  id: string;
  ts: string;
  type: AuditEventType;
  business_id: string;
  business_name: string;
  actor: string;
  summary: string;
  payload?: unknown;
}

const KEY = "msme-audit-log";
const listeners = new Set<() => void>();

function read(): AuditEvent[] {
  try {
    return JSON.parse(localStorage.getItem(KEY) ?? "[]") as AuditEvent[];
  } catch {
    return [];
  }
}

function write(events: AuditEvent[]) {
  localStorage.setItem(KEY, JSON.stringify(events));
  listeners.forEach((fn) => fn());
}

export function getAuditEvents(): AuditEvent[] {
  return read().sort((a, b) => b.ts.localeCompare(a.ts));
}

export function addAuditEvent(e: Omit<AuditEvent, "id" | "ts" | "actor">) {
  const events = read();
  events.push({
    ...e,
    id: `evt-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    ts: new Date().toISOString(),
    actor: "Credit Officer (demo)",
  });
  write(events);
}

export function subscribeAudit(fn: () => void): () => void {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

/** Seed a believable history the first time the app opens. */
export function seedAuditIfEmpty() {
  if (read().length > 0) return;
  const hoursAgo = (h: number) =>
    new Date(Date.now() - h * 3600_000).toISOString();
  const seed: AuditEvent[] = [
    {
      id: "evt-seed-1",
      ts: hoursAgo(26),
      type: "intake",
      business_id: "MSME007",
      business_name: "Nashik Agro Supply",
      actor: "Credit Officer (demo)",
      summary: "Documents verified — bank statement (12 mo) + GST summary. Readiness: green.",
      payload: { checks_passed: 6, checks_warned: 0, checks_failed: 0 },
    },
    {
      id: "evt-seed-2",
      ts: hoursAgo(25),
      type: "score",
      business_id: "MSME007",
      business_name: "Nashik Agro Supply",
      actor: "Analyst Agent",
      summary: "Financial health score computed from verified bank + GST data.",
      payload: { model: "XGBoost + SHAP", features_used: 20 },
    },
    {
      id: "evt-seed-3",
      ts: hoursAgo(24),
      type: "decision",
      business_id: "MSME007",
      business_name: "Nashik Agro Supply",
      actor: "Credit Officer (demo)",
      summary: "Approved — steady revenue, clean GST record. Reason: matches model suggestion.",
      payload: { decision: "Approved" },
    },
  ];
  write(seed);
}
