export type RiskBand = "Low" | "Medium" | "High";
export type ModelDecision = "Approve" | "Conditional Approval" | "Reject";
export type OfficerStatus =
  | "Pending"
  | "Approved"
  | "Conditional"
  | "Rejected"
  | "Info Requested";

export interface PortfolioRow {
  business_id: string;
  name: string;
  industry: string;
  city: string;
  state: string;
  category: "Micro" | "Small" | "Medium";
  gst_registered: boolean;
  score: number;
  band: RiskBand;
  confidence: number;
  avg_monthly_revenue: number;
  model_decision: ModelDecision;
  officer_status: OfficerStatus;
  applied_at: string;
}

/** One SHAP-ranked factor — mirrors the Agent 2 JSON contract (HANDOFF.md). */
export interface Factor {
  name: string;
  label: string;
  direction: "+" | "-";
  weight: number;
  detail: string;
}

export interface TrendPoint {
  month: string;
  revenue: number;
  expense: number;
}

export interface GstMonth {
  month: string;
  filed_on_time: boolean;
  late_days: number;
  filing_date: string;
  sales: number;
}

export interface KeyMetrics {
  cash_buffer_days: number;
  income_volatility: number;
  expense_ratio: number;
  bounce_count: number;
  emi_ratio: number;
  gst_regularity: number;
  digital_payment_ratio: number;
  revenue_growth: number;
  monthly_savings_rate: number;
  average_balance: number;
  minimum_balance: number;
}

export interface BusinessDetail {
  business_id: string;
  profile: {
    name: string;
    owner: string;
    industry: string;
    city: string;
    state: string;
    business_age_years: number;
    employee_count: number;
    category: "Micro" | "Small" | "Medium";
    gst_registered: boolean;
    existing_loan: boolean;
    existing_emi: number;
    annual_turnover: number;
  };
  score: { score: number; band: RiskBand; confidence: number };
  factors: Factor[];
  recommendation: {
    loan_amount: number;
    tenure_months: number;
    interest_band: string;
    decision: ModelDecision;
  };
  trends: TrendPoint[];
  gst_timeline: GstMonth[];
  metrics: KeyMetrics;
  officer_status: OfficerStatus;
  applied_at: string;
}
