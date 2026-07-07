import type { BusinessDetail } from "./api/types";

/**
 * The customer portal is a single-business persona demo.
 * All customer pages bind to this real business from the scored dataset,
 * so every number shown matches what the officer side computes for it.
 */
export const DEMO_BUSINESS_ID = "MSME014";

export function gradeFromScore(score: number): string {
  if (score >= 90) return "A+";
  if (score >= 80) return "A";
  if (score >= 70) return "B+";
  if (score >= 60) return "B";
  if (score >= 45) return "C";
  return "D";
}

/** Map raw model metrics onto 0-100 category axes for radar/report charts. */
export function categoryScores(d: BusinessDetail) {
  const m = d.metrics;
  const clamp = (v: number) => Math.max(0, Math.min(100, Math.round(v)));
  return [
    { name: "Cash Flow", score: clamp((1 - m.expense_ratio) * 100 + 50) },
    { name: "GST Compliance", score: clamp(m.gst_regularity * 100) },
    { name: "Growth", score: clamp(50 + m.revenue_growth * 100) },
    { name: "Digital Payments", score: clamp(m.digital_payment_ratio * 100) },
    { name: "Stability", score: clamp((1 - m.income_volatility) * 100) },
  ];
}
