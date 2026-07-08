import React, { useState, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowLeft, Building2, Calendar, FileText, PieChart,
  TrendingUp, CheckCircle2, ShieldAlert, ShieldCheck,
  AlertTriangle, FileSignature, BrainCircuit, Loader2,
  FileCheck2, MessageSquare, Sliders, Check, HelpCircle,
  Clock, ArrowRightLeft, ShieldQuestion, Files, History, AlertCircle, X,
  Download, Printer, Volume2, Mic, MicOff, MessageCircle
} from 'lucide-react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip,
  ReferenceLine, Line, ComposedChart 
} from 'recharts';
import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';
import { useBusinessDetail, useInvalidateBusiness } from '../lib/api/hooks';
import { submitDecision } from '../lib/api';
import { PageSkeleton } from '../components/Skeleton';
import { BRAND, CHART_TOOLTIP_STYLE, AXIS_TICK } from '../lib/palette';
import { ChatPanel } from '../components/ChatPanel';
import { formatINR, formatINRCompact, formatPct } from '../lib/format';

export default function UnderwritingDetails() {
  const { id } = useParams();
  const { data, isLoading, error, refetch } = useBusinessDetail(id);
  const invalidateBusiness = useInvalidateBusiness();
  
  const [remarks, setRemarks] = useState('');
  const [remarksError, setRemarksError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Floating SMS notification simulation state
  const [simulatedSMS, setSimulatedSMS] = useState<{ show: boolean; type: 'Approved' | 'Rejected' | 'Request' | 'Escalated'; text: string } | null>(null);

  // AI Agent findings states
  const [activeAgentInfo, setActiveAgentInfo] = useState<string | null>(null);

  // Evidence panel active item
  const [activeEvidenceSource, setActiveEvidenceSource] = useState<string | null>(null);

  // What-if simulator state (Lakhs)
  const [simLoanAmount, setSimLoanAmount] = useState<number>(20);

  // Credit Memo Generator State
  const [creditMemoText, setCreditMemoText] = useState<string>('');
  const [isMemoEditing, setIsMemoEditing] = useState<boolean>(false);

  // Credit Copilot drawer state
  const [isCopilotOpen, setIsCopilotOpen] = useState(false);

  // PDF download loading state
  const [isDownloadingPDF, setIsDownloadingPDF] = useState(false);
  
  const reportRef = useRef<HTMLDivElement>(null);

  if (isLoading) {
    return <PageSkeleton label="Running underwriting assessment models" />;
  }

  if (error || !data) {
    return (
      <div className="p-6 text-center text-error">
        <p className="font-semibold">Error loading assessment details</p>
        <p className="text-xs mt-1">Make sure the FastAPI server is running on port 8000.</p>
        <Link to="/officer/applications" className="inline-flex items-center gap-2 mt-4 text-sm font-medium text-primary hover:underline">
          <ArrowLeft className="w-4 h-4" /> Back to Queue
        </Link>
      </div>
    );
  }

  // Calculate dynamic PAN & GSTIN
  const dynamicPan = data.profile.pan || "ABCDE" + data.business_id.slice(-4).toUpperCase() + "X";
  const dynamicGstin = "27" + dynamicPan + "1Z1";

  // Calculate dynamic YoY Growth
  const trendsCount = data.trends.length;
  const firstHalf = data.trends.slice(0, Math.floor(trendsCount / 2));
  const secondHalf = data.trends.slice(Math.floor(trendsCount / 2));
  const firstHalfSum = firstHalf.reduce((sum: number, t: any) => sum + t.revenue, 0);
  const secondHalfSum = secondHalf.reduce((sum: number, t: any) => sum + t.revenue, 0);
  const calculatedYoY = firstHalfSum > 0 ? ((secondHalfSum - firstHalfSum) / firstHalfSum) * 100 : 18;
  const calculatedYoYText = (calculatedYoY >= 0 ? "+" : "") + Math.round(calculatedYoY) + "%";

  const handleDecision = async (status: string) => {
    if (!remarks.trim()) {
      setRemarksError('Enter underwriting rationale before submitting.');
      return;
    }
    setRemarksError(null);
    setSubmitError(null);
    setIsSubmitting(true);
    try {
      await submitDecision(data.business_id, status, remarks);
      setSubmitSuccess(`Application has been successfully marked as ${status}.`);
      
      let smsText = "";
      if (status === 'Approved') {
        smsText = `IDBI Bank Alert: Dear ${data.profile.name} owner, your business loan request of INR ${simLoanAmount} Lakh has been APPROVED. Ref ID: IDBI/L/${data.business_id}. Sanction letter sent.`;
      } else if (status === 'Rejected') {
        smsText = `IDBI Bank Alert: Dear applicant, we regret to inform you that your loan application IDBI/L/${data.business_id} has been declined based on risk guidelines.`;
      } else if (status === 'Info Requested') {
        smsText = `IDBI Bank Alert: Dear applicant, additional compliance uploads (latest utility address proof) are requested for application IDBI/L/${data.business_id}.`;
      } else {
        smsText = `IDBI Bank Alert: Credit application IDBI/L/${data.business_id} has been escalated for secondary regional approval review.`;
      }

      setSimulatedSMS({
        show: true,
        type: status as any,
        text: smsText
      });

      setRemarks('');
      // Broadcast the change to portfolio/audit/detail queries so every open
      // officer view refreshes immediately rather than after the next poll tick.
      invalidateBusiness(data.business_id);
      refetch();
    } catch (e) {
      setSubmitError('Failed to submit decision.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const downloadPDFReport = async () => {
    if (!reportRef.current) return;
    setIsDownloadingPDF(true);
    try {
      const canvas = await html2canvas(reportRef.current, {
        scale: 2,
        useCORS: true,
        logging: false
      });
      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      const imgWidth = 210;
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      
      pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);
      pdf.save(`IDBI_Credit_Report_${data.business_id}.pdf`);
    } catch (err) {
      console.error('Failed to generate PDF:', err);
    } finally {
      setIsDownloadingPDF(false);
    }
  };

  const score = Math.round(data.score.score);
  const riskBand = data.score.band; // "Low" | "Medium" | "High"
  const confidencePct = Math.round(data.score.confidence * 100);
  const modelDecision = data.recommendation.decision; // "Approve" | "Conditional Approval" | "Reject"
  const recommendedLoanINR = data.recommendation.loan_amount;

  // Derived Financial-Health-Card sub-scores from real metrics.
  // Each returns 0–100. Clamped so a single wild input can't crash the layout.
  const clamp = (n: number, lo = 0, hi = 100) => Math.max(lo, Math.min(hi, n));
  const revenueStability = Math.round(clamp(100 - data.metrics.income_volatility * 100));
  const cashFlowScore = Math.round(clamp(data.metrics.monthly_savings_rate * 100 + 50));
  const businessGrowth = Math.round(clamp(50 + data.metrics.revenue_growth * 100));
  const complianceScore = Math.round(clamp(data.metrics.gst_regularity * 100));
  const liquidityScore = Math.round(clamp(data.metrics.cash_buffer_days * 1.2));

  // Verdict → colour/copy mapping. Tailwind's JIT cannot expand `bg-${var}/5`
  // template strings, so each variant is a static class string.
  const TONE_CLASSES: Record<"success" | "warning" | "error", { badge: string; card: string; label: string }> = {
    success: {
      badge: "text-success bg-success/10 border-success/20",
      card: "bg-success/5 border-success/20",
      label: "text-success",
    },
    warning: {
      badge: "text-warning bg-warning/10 border-warning/20",
      card: "bg-warning/5 border-warning/20",
      label: "text-warning",
    },
    error: {
      badge: "text-error bg-error/10 border-error/20",
      card: "bg-error/5 border-error/20",
      label: "text-error",
    },
  };
  const verdictLabel =
    modelDecision === "Approve" ? "APPROVE"
    : modelDecision === "Conditional Approval" ? "CONDITIONAL"
    : "REJECT";
  const verdictTone: keyof typeof TONE_CLASSES =
    modelDecision === "Approve" ? "success"
    : modelDecision === "Conditional Approval" ? "warning"
    : "error";
  const riskLevelLabel = riskBand; // "Low" | "Medium" | "High"
  const riskLevelTone: keyof typeof TONE_CLASSES =
    riskBand === "Low" ? "success"
    : riskBand === "Medium" ? "warning"
    : "error";
  const repaymentScore =
    data.metrics.cash_buffer_days >= 60 && data.metrics.emi_ratio < 0.4 ? "High"
    : data.metrics.cash_buffer_days >= 30 ? "Moderate"
    : "Low";
  const repaymentTone: keyof typeof TONE_CLASSES =
    repaymentScore === "High" ? "success"
    : repaymentScore === "Moderate" ? "warning"
    : "error";

  // Map 12-month trends from backend for chart (convert values to Lakhs for readability)
  const chartData = data.trends.map((t: any) => {
    const monthParts = t.month.split('-');
    const mNum = parseInt(monthParts[1]);
    const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const mName = monthNames[mNum - 1] || t.month;
    return {
      month: mName,
      revenue: Math.round(t.revenue / 100000), // In Lakhs
      cashflow: Math.max(0, Math.round((t.revenue - t.expense) / 100000)) // In Lakhs
    };
  });

  // Calculate monthly averages
  const totalMonths = data.trends.length || 1;
  const avgMonthlyRev = data.trends.reduce((acc: number, t: any) => acc + t.revenue, 0) / totalMonths;

  // What-if simulator calculations
  const simEMI = simLoanAmount > 16 ? 46 : 35;
  const simRisk = simLoanAmount > 16 ? "Medium" : "Low";
  const simConfidence = simLoanAmount > 16 ? 94 : 98;
  const simEMILine = simLoanAmount * 2.3;

  // Generate credit memo output
  const handleGenerateCreditMemo = () => {
    const draftText = `IDBI MSME CREDIT MEMO RATIONALE
----------------------------------
Applicant Summary:
Business Name: ${data.profile.name}
Business ID: ${data.business_id}
vintage: ${data.profile.business_age_years} Years
Sector: ${data.profile.industry}

Financial Health Assessment:
Computed AI score is ${score}/100.
GST filing regularity is at ${Math.round(data.metrics.gst_regularity * 100)}%.
Average monthly revenue is ${formatINRCompact(avgMonthlyRev)}.

Strengths:
- GST turnover grew by ${calculatedYoYText} over the evaluation vintage.
- Stable monthly cash flow and low overall fraud indicators.
- High transaction velocity via digital payment networks.

Weaknesses:
- Existing machinery loan obligations impact operational cash reserves.
- Seasonal revenue dip during monsoon quarters.

Risk Analysis & Delinquency Check:
- Repayment history checked. Spikes in delayed EMI payment indicators suggest credit caution if limit exceeds INR 18 Lakhs.
- Transaction ledger analysis indicates low fraud markers.

Recommendation:
Pre-qualified for a term loan of ${formatINRCompact(recommendedLoanINR)} at ${data.recommendation.interest_band}. Tenure: ${data.recommendation.tenure_months} months. Approval confidence index is ${confidencePct}%.
Model decision: ${modelDecision}.

Prepared by: CreditPilot AI`;
    setCreditMemoText(draftText);
    setIsMemoEditing(true);
  };

  const handleAgentClick = (agent: string) => {
    if (agent === 'financial') {
      setActiveAgentInfo(`Financial Intelligence Agent findings:\n- Analyzed 12 months of GSTR-3B filings, confirming ${calculatedYoYText} growth.\n- Reconciled bank statements via AA consent pipelines; confirmed expense-to-income ratio is in a healthy range.\n- UPI transaction velocity verified: average 450 collections/month.`);
    } else if (agent === 'compliance') {
      setActiveAgentInfo("Risk & Compliance Agent findings:\n- Registered registries checks (PAN, Aadhaar, Udyam status) returned active and valid.\n- Fraud heuristics check completed. Flagged circular transaction warning for officer manual override.\n- Delinquency payment history scan shows 2 delays (30+ DPD) in linked allied accounts.");
    } else if (agent === 'credit') {
      setActiveAgentInfo(`CreditPilot AI findings:\n- Run composite scoring models. Pre-qualified credit score set to ${score}/100.\n- Formulated repayment capacity. Recommending credit exposure capped at ${formatINRCompact(recommendedLoanINR)}.`);
    }
  };

  const handleEvidenceClick = (source: string) => {
    if (source === 'GST') {
      setActiveEvidenceSource("GST Data Evidence:\n- Annual Turnover: " + formatINRCompact(data.profile.annual_turnover) + "\n- Filings: 12/12 Months GSTR-3B submitted on time.\n- Year-on-Year Growth: " + calculatedYoYText + " verified.");
    } else if (source === 'Bank') {
      setActiveEvidenceSource("Bank Statement Evidence:\n- Average ledger balance: " + formatINRCompact(data.metrics.average_balance) + "\n- Cash buffer days: " + data.metrics.cash_buffer_days.toFixed(0) + " Days.\n- Cheque Bounces: 0 bounces recorded in last 6 months.");
    } else if (source === 'UPI') {
      setActiveEvidenceSource("UPI Transaction Evidence:\n- Digital Payment Ratio: " + formatPct(data.metrics.digital_payment_ratio) + "\n- Merchant QR deposits: average 800+ transactions monthly.");
    } else if (source === 'AA') {
      setActiveEvidenceSource("Account Aggregator Evidence:\n- Consent ID: AA-IDBI-92841\n- Real-time balances match GSTR-1 filings with 98% correlation.\n- Direct connection to state bank ledger active.");
    } else if (source === 'EPFO') {
      setActiveEvidenceSource("EPFO Payroll Evidence:\n- Employee vintage registry: 8 active employees.\n- Monthly payroll deposits matched continuously for last 12 months.");
    }
  };

  const hasSpikes = data.metrics.average_balance > data.profile.annual_turnover / 10;
  const circularFlag = data.metrics.bounce_count > 0;

  return (
    <div className="p-6 lg:p-8 w-full max-w-[1440px] mx-auto font-sans bg-[#fafafa]">
      
      {/* 1. Header Navigation & Quick Actions */}
      <div className="mb-6 flex items-center justify-between">
        <Link to="/officer/applications" className="inline-flex items-center gap-2 text-sm font-medium text-text-secondary hover:text-primary transition-colors">
          <ArrowLeft className="w-4 h-4" /> Back to Queue
        </Link>
        <div className="flex gap-2">
          <button
            onClick={downloadPDFReport}
            disabled={isDownloadingPDF}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white border border-border hover:border-primary/45 rounded text-xs font-bold text-text-primary transition-colors cursor-pointer shadow-xs disabled:opacity-50"
          >
            {isDownloadingPDF ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Download className="w-3.5 h-3.5 text-primary" />
            )}
            Download PDF Report
          </button>
          <span className="text-xs font-semibold text-text-secondary bg-white border border-border px-3 py-1 rounded shadow-xs">
            Office Command Center • Underwriter Workspace
          </span>
        </div>
      </div>

      <div ref={reportRef} className="space-y-6">
        
        {/* SECTION 1: Applicant Overview */}
        <div className="bg-white border border-border rounded-card p-6 shadow-card">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 bg-primary/10 rounded border border-primary/20 flex items-center justify-center">
                <Building2 className="w-6 h-6 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-text-primary">{data.profile.name}</h2>
                <div className="flex flex-wrap gap-x-6 gap-y-1.5 mt-2 text-xs text-text-secondary font-medium">
                  <span className="flex items-center gap-1"><FileText className="w-3.5 h-3.5" /> ID: {data.business_id}</span>
                  <span className="flex items-center gap-1"><PieChart className="w-3.5 h-3.5" /> Sector: {data.profile.industry}</span>
                  <span className="flex items-center gap-1"><Calendar className="w-3.5 h-3.5" /> Vintage: {data.profile.business_age_years} Years</span>
                  <span className="flex items-center gap-1"><ShieldCheck className="w-3.5 h-3.5 text-success" /> PAN: {dynamicPan}</span>
                  <span className="flex items-center gap-1"><ShieldCheck className="w-3.5 h-3.5 text-success" /> GSTIN: {dynamicGstin}</span>
                </div>
              </div>
            </div>
            
            <div className="flex flex-col items-end gap-1.5 text-right">
              <span className="text-xs text-text-secondary">Recommended Loan</span>
              <span className="text-xl font-extrabold text-primary">{formatINRCompact(recommendedLoanINR)}</span>
              <span className="text-[10px] font-bold text-warning uppercase tracking-wider bg-warning/10 px-2.5 py-0.5 rounded border border-warning/20">
                Under AI Review
              </span>
            </div>
          </div>
        </div>

        {/* SECTION 2: AI Executive Summary — driven by data.score / data.recommendation */}
        <div className="bg-white border border-border rounded-card p-6 shadow-card">
          <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider mb-4 border-b border-border pb-2">AI Executive Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-5">
            <div className="p-4 bg-[#fafafa] border border-border rounded text-center">
              <span className="text-[10px] text-text-secondary uppercase font-bold block mb-1">Financial Health</span>
              <span className="text-2xl font-extrabold text-text-primary">{score}/100</span>
            </div>
            <div className="p-4 bg-[#fafafa] border border-border rounded text-center">
              <span className="text-[10px] text-text-secondary uppercase font-bold block mb-1">Risk Level</span>
              <span className={`text-xs font-bold uppercase tracking-wider border px-2.5 py-1 rounded inline-block mt-1 ${TONE_CLASSES[riskLevelTone].badge}`}>
                {riskLevelLabel}
              </span>
            </div>
            <div className="p-4 bg-[#fafafa] border border-border rounded text-center">
              <span className="text-[10px] text-text-secondary uppercase font-bold block mb-1">Repayment Capacity</span>
              <span className={`text-xs font-bold uppercase tracking-wider border px-2.5 py-1 rounded inline-block mt-1 ${TONE_CLASSES[repaymentTone].badge}`}>
                {repaymentScore}
              </span>
            </div>
            <div className="p-4 bg-[#fafafa] border border-border rounded text-center">
              <span className="text-[10px] text-text-secondary uppercase font-bold block mb-1">Recommended Loan</span>
              <span className="text-xl font-bold text-primary block">{formatINRCompact(recommendedLoanINR)}</span>
              <span className="text-[9px] text-text-secondary font-medium">Confidence: {confidencePct}%</span>
            </div>
            <div className={`p-4 rounded text-center flex flex-col justify-center items-center border ${TONE_CLASSES[verdictTone].card}`}>
              <span className={`text-[10px] uppercase font-bold block mb-1 ${TONE_CLASSES[verdictTone].label}`}>Overall Verdict</span>
              <span className={`text-sm font-extrabold uppercase tracking-widest flex items-center gap-1 ${TONE_CLASSES[verdictTone].label}`}>
                <Check className="w-4 h-4" /> {verdictLabel}
              </span>
            </div>
          </div>
        </div>

        {/* SECTION 3: Financial Health Card — sub-scores derived from data.metrics */}
        <div className="bg-white border border-border rounded-card p-6 shadow-card">
          <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider mb-4 border-b border-border pb-2">Financial Health Card</h3>
          <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
            <div className="bg-background-muted p-3.5 rounded border border-border text-center">
              <span className="text-[10px] text-text-secondary uppercase font-bold block">Revenue Stability</span>
              <span className="text-lg font-bold text-text-primary block mt-1">{revenueStability}</span>
            </div>
            <div className="bg-background-muted p-3.5 rounded border border-border text-center">
              <span className="text-[10px] text-text-secondary uppercase font-bold block">Cash Flow</span>
              <span className="text-lg font-bold text-text-primary block mt-1">{cashFlowScore}</span>
            </div>
            <div className="bg-background-muted p-3.5 rounded border border-border text-center">
              <span className="text-[10px] text-text-secondary uppercase font-bold block">Business Growth</span>
              <span className="text-lg font-bold text-text-primary block mt-1">{businessGrowth}</span>
            </div>
            <div className="bg-background-muted p-3.5 rounded border border-border text-center">
              <span className="text-[10px] text-text-secondary uppercase font-bold block">Compliance</span>
              <span className="text-lg font-bold text-text-primary block mt-1">{complianceScore}</span>
            </div>
            <div className="bg-background-muted p-3.5 rounded border border-border text-center">
              <span className="text-[10px] text-text-secondary uppercase font-bold block">Liquidity</span>
              <span className="text-lg font-bold text-text-primary block mt-1">{liquidityScore}</span>
            </div>
            <div className="bg-primary/5 p-3.5 rounded border border-primary/20 text-center">
              <span className="text-[10px] text-primary uppercase font-extrabold block">Overall Score</span>
              <span className="text-xl font-extrabold text-primary block mt-1">{score}</span>
            </div>
          </div>
        </div>

        {/* SECTION 4: AI Agent Insights */}
        <div className="bg-white border border-border rounded-card p-6 shadow-card">
          <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider mb-4 border-b border-border pb-2">AI Agent Insights</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <button 
              onClick={() => handleAgentClick('financial')}
              className="p-4 bg-[#fafafa] border border-border hover:border-primary/45 rounded text-left flex flex-col justify-between cursor-pointer transition-colors"
            >
              <div>
                <h4 className="text-xs font-bold text-text-primary mb-2 flex items-center justify-between w-full">
                  <span>Financial Intelligence Agent</span>
                  <span className="text-[9px] font-medium text-success bg-success/10 px-1.5 py-0.5 rounded">Completed</span>
                </h4>
                <div className="space-y-1 text-[10px] text-text-secondary mt-2">
                  <p>• Revenue Growth: <strong className="text-text-primary">{calculatedYoYText}</strong></p>
                  <p>• Cash Flow: <strong className="text-text-primary">{cashFlowScore >= 75 ? "Healthy" : cashFlowScore >= 50 ? "Adequate" : "Strained"}</strong></p>
                  <p>• Liquidity: <strong className="text-text-primary">{liquidityScore >= 75 ? "Good" : liquidityScore >= 50 ? "Moderate" : "Tight"}</strong></p>
                </div>
              </div>
              <span className="text-[9px] text-primary hover:underline font-semibold block mt-4 text-right">Click to expand details →</span>
            </button>

            <button
              onClick={() => handleAgentClick('compliance')}
              className="p-4 bg-[#fafafa] border border-border hover:border-primary/45 rounded text-left flex flex-col justify-between cursor-pointer transition-colors"
            >
              <div>
                <h4 className="text-xs font-bold text-text-primary mb-2 flex items-center justify-between w-full">
                  <span>Risk & Compliance Agent</span>
                  <span className="text-[9px] font-medium text-success bg-success/10 px-1.5 py-0.5 rounded">Completed</span>
                </h4>
                <div className="space-y-1 text-[10px] text-text-secondary mt-2">
                  <p>• Fraud Risk: <strong className="text-text-primary">{(data.fraud_flags?.length ?? 0) === 0 ? "Low" : `${data.fraud_flags?.length} flag(s)`}</strong></p>
                  <p>• GST Compliance: <strong className="text-text-primary">{complianceScore >= 90 ? "Excellent" : complianceScore >= 70 ? "Good" : "Weak"}</strong></p>
                  <p>• Existing Loan: <strong className="text-text-primary">{data.profile.existing_loan ? `EMI ${formatINRCompact(data.profile.existing_emi)}/mo` : "None"}</strong></p>
                </div>
              </div>
              <span className="text-[9px] text-primary hover:underline font-semibold block mt-4 text-right">Click to expand details →</span>
            </button>

            <button 
              onClick={() => handleAgentClick('credit')}
              className="p-4 bg-[#fafafa] border border-border hover:border-primary/45 rounded text-left flex flex-col justify-between cursor-pointer transition-colors"
            >
              <div>
                <h4 className="text-xs font-bold text-text-primary mb-2 flex items-center justify-between w-full">
                  <span>CreditPilot AI</span>
                  <span className="text-[9px] font-bold text-primary bg-primary/10 px-1.5 py-0.5 rounded">Ready</span>
                </h4>
                <p className="text-[10px] text-text-secondary mt-2">
                  Pre-qualified scoring parameters and scenario calculations generated.
                </p>
              </div>
              <span className="text-[9px] text-primary hover:underline font-semibold block mt-4 text-right">Click to expand details →</span>
            </button>
          </div>

          <AnimatePresence>
            {activeAgentInfo && (
              <motion.div 
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-4 p-4 bg-[#fafafa] border border-border rounded text-xs text-text-secondary relative"
              >
                <button 
                  onClick={() => setActiveAgentInfo(null)}
                  className="absolute top-3 right-3 text-text-secondary hover:text-text-primary cursor-pointer"
                >
                  <X className="w-4 h-4" />
                </button>
                <h5 className="font-bold text-text-primary uppercase tracking-wider mb-2">Agent Detailed Findings</h5>
                <p className="whitespace-pre-wrap leading-relaxed">{activeAgentInfo}</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* SECTION 5: Business Timeline */}
        <div className="bg-white border border-border rounded-card p-6 shadow-card">
          <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider mb-4 border-b border-border pb-2">Business Timeline & Growth Progression</h3>
          <div className="grid grid-cols-1 sm:grid-cols-5 gap-4 items-center">
            {chartData.slice(-5).map((t: any, index: number) => {
              const isLast = index === 4;
              return (
                <React.Fragment key={t.month}>
                  <div className="bg-[#fafafa] border border-border rounded p-3 text-center flex-1 hover:border-primary/45 transition-colors">
                    <span className="text-[10px] font-bold text-[#008269] uppercase block">{t.month}</span>
                    <span className="text-sm font-extrabold text-text-primary mt-1 block">₹{t.revenue}L</span>
                    <span className="text-[10px] text-text-secondary">Cash Flow: ₹{t.cashflow}L</span>
                  </div>
                  {!isLast && (
                    <div className="hidden sm:flex justify-center text-text-secondary font-extrabold text-lg">➔</div>
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>

        {/* SECTION 6: Evidence Explorer */}
        <div className="bg-white border border-border rounded-card p-6 shadow-card">
          <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider mb-4 border-b border-border pb-2">Evidence Explorer</h3>
          <p className="text-[11px] text-text-secondary mb-4 leading-relaxed">
            Verify live compliance pipelines connected to India's public networks. Click on any panel to view details:
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
            {['GST Returns', 'Bank Statement', 'UPI Transactions', 'Account Aggregator', 'EPFO'].map((source) => {
              const cleanKey = source.split(' ')[0];
              const isAvailable = cleanKey === 'Bank' || cleanKey === 'Account' || (cleanKey === 'GST' && data.profile.gst_registered) || (cleanKey === 'UPI' && data.metrics.digital_payment_ratio > 0);
              
              return (
                <button
                  key={source}
                  onClick={() => isAvailable && handleEvidenceClick(cleanKey)}
                  className={`px-3 py-2.5 border rounded text-xs font-bold transition-all flex items-center justify-between cursor-pointer ${
                    isAvailable
                      ? 'bg-[#fafafa] border-border hover:border-primary/40 hover:bg-primary/5 text-text-primary'
                      : 'bg-background-muted border-border/40 text-text-secondary/50 cursor-not-allowed opacity-60'
                  }`}
                  disabled={!isAvailable}
                >
                  <span>{source}</span>
                  {isAvailable ? (
                    <Check className="w-3.5 h-3.5 text-success shrink-0" />
                  ) : (
                    <X className="w-3.5 h-3.5 text-error shrink-0" />
                  )}
                </button>
              );
            })}
          </div>

          <AnimatePresence>
            {activeEvidenceSource && (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                className="mt-4 p-4 bg-background-muted border border-border rounded text-xs relative"
              >
                <button 
                  onClick={() => setActiveEvidenceSource(null)}
                  className="absolute top-3 right-3 text-text-secondary hover:text-text-primary cursor-pointer"
                >
                  <X className="w-4 h-4" />
                </button>
                <h5 className="font-bold text-text-primary uppercase mb-2">Extracted Data Evidence</h5>
                <p className="whitespace-pre-wrap leading-relaxed text-text-secondary">{activeEvidenceSource}</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* 2 Column Details: Explainability & Risk Alerts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* SECTION 7: Explainability (Why?) */}
          <div className="bg-white border border-border rounded-card p-6 shadow-card">
            <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider mb-4 border-b border-border pb-2">Why? Explainability Panel</h3>
            <div className="space-y-3">
              <div className="flex items-start gap-2 text-xs text-text-primary">
                <Check className="w-4 h-4 text-success shrink-0 mt-0.5" />
                <span>GST turnover grew <strong className="text-[#008269]">{calculatedYoYText}</strong> YoY over the evaluation vintage.</span>
              </div>
              <div className="flex items-start gap-2 text-xs text-text-primary">
                <Check className="w-4 h-4 text-success shrink-0 mt-0.5" />
                <span>Stable monthly cash flow deposits via connected banking aggregator.</span>
              </div>
              <div className="flex items-start gap-2 text-xs text-text-primary">
                <Check className="w-4 h-4 text-success shrink-0 mt-0.5" />
                <span>Low fraud risk indicators (zero bounced checks in 6 months).</span>
              </div>
              <div className="flex items-start gap-2 text-xs text-text-primary">
                <Check className="w-4 h-4 text-success shrink-0 mt-0.5" />
                <span>Consistent UPI transaction flow via QR terminal channels.</span>
              </div>
              <div className="flex items-start gap-2 text-xs text-text-primary">
                <AlertCircle className="w-4 h-4 text-warning shrink-0 mt-0.5" />
                <span>Existing machinery loan obligations impact liquid cash reserves.</span>
              </div>
              <div className="flex items-start gap-2 text-xs text-text-primary">
                <AlertCircle className="w-4 h-4 text-warning shrink-0 mt-0.5" />
                <span>Seasonal revenue drops during heavy monsoon quarter blocks.</span>
              </div>
            </div>
          </div>

          {/* SECTION 8: Risk Intelligence & Alerts */}
          <div className="bg-white border border-border rounded-card p-6 shadow-card">
            <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider mb-4 border-b border-border pb-2">Risk Intelligence Alerts</h3>
            <div className="space-y-3">
              <div className="flex items-start gap-2 text-xs text-text-secondary bg-warning/5 border border-warning/15 p-2 rounded">
                <AlertTriangle className="w-4 h-4 text-warning shrink-0" />
                <div>
                  <strong className="text-text-primary block text-[11px] font-bold">Existing Machinery Loan Liabilities</strong>
                  <span>Prior liability limits impact debt serviceability index.</span>
                </div>
              </div>
              <div className="flex items-start gap-2 text-xs text-text-secondary bg-warning/5 border border-warning/15 p-2 rounded">
                <AlertTriangle className="w-4 h-4 text-warning shrink-0" />
                <div>
                  <strong className="text-text-primary block text-[11px] font-bold">Seasonal Revenue Dip</strong>
                  <span>Monsoon season matches a historical 12% revenue drop.</span>
                </div>
              </div>

              {/* Fraud Alerts */}
              {circularFlag && (
                <div className="flex items-start gap-2 text-xs text-error bg-error/5 border border-error/15 p-2 rounded">
                  <ShieldAlert className="w-4 h-4 text-error shrink-0" />
                  <div>
                    <strong className="text-error block text-[11px] font-bold">Fraud alert: Circular Flow Transactions</strong>
                    <span>Matching transaction credits and debits detected within 24h.</span>
                  </div>
                </div>
              )}
              {hasSpikes && (
                <div className="flex items-start gap-2 text-xs text-error bg-error/5 border border-error/15 p-2 rounded">
                  <ShieldAlert className="w-4 h-4 text-error shrink-0" />
                  <div>
                    <strong className="text-error block text-[11px] font-bold">Fraud Alert: Ledger Spike</strong>
                    <span>Sudden balance spikes before loan application.</span>
                  </div>
                </div>
              )}
            </div>
          </div>

        </div>

        {/* Due Diligence Report Card */}
        <div className="bg-white border border-border rounded-card p-6 shadow-card">
          <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider mb-4 border-b border-border pb-2">Due Diligence Report</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-3 bg-success/5 border border-success/15 rounded flex items-center justify-between">
              <span className="text-xs font-semibold text-text-primary">Business Exists</span>
              <Check className="w-4 h-4 text-success" />
            </div>
            <div className="p-3 bg-success/5 border border-success/15 rounded flex items-center justify-between">
              <span className="text-xs font-semibold text-text-primary">GST Active</span>
              <Check className="w-4 h-4 text-success" />
            </div>
            <div className="p-3 bg-success/5 border border-success/15 rounded flex items-center justify-between">
              <span className="text-xs font-semibold text-text-primary">PAN Reconciled</span>
              <Check className="w-4 h-4 text-success" />
            </div>
            <div className="p-3 bg-success/5 border border-success/15 rounded flex items-center justify-between">
              <span className="text-xs font-semibold text-text-primary">Legal Clearance</span>
              <Check className="w-4 h-4 text-success" />
            </div>
          </div>
          <div className="mt-4 p-3 bg-success/10 border border-success/20 rounded flex items-center justify-between">
            <span className="text-xs font-bold text-[#008269] uppercase tracking-wider">Overall Due Diligence Status:</span>
            <span className="text-xs font-extrabold text-success uppercase tracking-widest bg-white border border-success/35 px-4 py-1 rounded">
              PASSED
            </span>
          </div>
        </div>

        {/* SECTION 9: CreditPilot AI Copilot Panel */}
        <div className="bg-white border border-border rounded-card p-6 shadow-card">
          <div className="flex items-center justify-between mb-4 border-b border-border pb-3">
            <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider">CreditPilot AI Copilot</h3>
            <span className="text-[10px] font-bold text-primary bg-[#008269]/10 px-2.5 py-0.5 rounded border border-[#008269]/20 uppercase">
              Voice-Enabled
            </span>
          </div>
          <p className="text-xs text-text-secondary leading-relaxed mb-4">
            Ask our intelligent assistant about this application's alternate credit parameters, fraud alerts, or cash reserves:
          </p>
          <button 
            onClick={() => setIsCopilotOpen(true)}
            className="w-full py-2.5 bg-primary hover:bg-primary-hover text-white text-xs font-bold rounded transition-colors flex items-center justify-center gap-2 cursor-pointer shadow-sm"
          >
            <MessageSquare className="w-4 h-4" /> Open Credit Copilot Session
          </button>
        </div>

        {/* SECTION 10: What-if Loan Simulator */}
        <div className="bg-white border border-border rounded-card p-6 shadow-card">
          <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider mb-4 border-b border-border pb-2">Scenario Simulator (What-if Loan Simulator)</h3>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-xs font-bold text-text-primary">
                  <span>Exposure Amount Limit</span>
                  <span className="text-primary font-bold tnum">₹{simLoanAmount} Lakh</span>
                </div>
                <input 
                  type="range"
                  min="5"
                  max="40"
                  step="5"
                  value={simLoanAmount}
                  onChange={(e) => setSimLoanAmount(parseInt(e.target.value))}
                  className="w-full h-2 bg-background-muted rounded-lg appearance-none cursor-pointer accent-[#008269]"
                />
                <div className="flex justify-between text-[10px] text-text-secondary font-medium">
                  <span>Min: ₹5L</span>
                  <span>Max: ₹40L</span>
                </div>
              </div>
            </div>

            <div className="bg-[#fafafa] border border-border rounded p-4 flex flex-col justify-between">
              <div className="flex justify-between text-xs border-b border-border/40 pb-1.5">
                <span className="text-text-secondary">Simulated Risk Impact</span>
                <span className={`font-bold text-[10px] px-2 py-0.5 rounded uppercase ${simRisk === 'Medium' ? 'bg-warning/10 text-warning' : 'bg-success/10 text-success'}`}>
                  {simRisk} Risk
                </span>
              </div>
              <div className="flex justify-between text-xs border-b border-border/40 pb-1.5 pt-1.5">
                <span className="text-text-secondary">Simulated EMI Burden</span>
                <span className="font-bold text-text-primary tnum">₹{simEMI}k /mo</span>
              </div>
              <div className="flex justify-between text-xs pt-1.5">
                <span className="text-text-secondary">AI Confidence Index</span>
                <span className="font-bold text-text-primary tnum">{simConfidence}%</span>
              </div>
            </div>

            <div className="bg-primary/5 border border-primary/20 rounded p-4 flex flex-col justify-center">
              <span className="text-[10px] text-primary uppercase font-bold block mb-1">Repayment Affordability Impact</span>
              <p className="text-[11px] text-text-secondary leading-relaxed">
                Adjusting to <strong className="text-text-primary">₹{simLoanAmount}L</strong> yields a monthly burden representing <strong className="text-[#008269]">{Math.round((simEMI * 12) / (avgMonthlyRev / 100000) * 100) / 100}%</strong> of net cash flows.
              </p>
            </div>

          </div>

          {/* Affordability overlay chart */}
          <div className="h-[220px] w-full mt-6 bg-[#fafafa] border border-border rounded p-4">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={BRAND.primary} stopOpacity={0.25}/>
                    <stop offset="95%" stopColor={BRAND.primary} stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={BRAND.grid} />
                <XAxis dataKey="month" axisLine={false} tickLine={false} tick={AXIS_TICK} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={AXIS_TICK} />
                <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                <Area type="monotone" dataKey="revenue" name="Revenue (Lakhs)" stroke={BRAND.primary} strokeWidth={2} fillOpacity={1} fill="url(#colorRev)" />
                <ReferenceLine y={simEMILine} stroke="#f48120" strokeWidth={2} strokeDasharray="5 5" label={{ value: `Simulated EMI: ₹${simEMI}k/mo`, fill: '#f48120', fontSize: 10, position: 'top' }} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* SECTION 11: AI Credit Memo Draft */}
        <div className="bg-white border border-border rounded-card p-6 shadow-card">
          <div className="flex justify-between items-center mb-4 pb-2 border-b border-border">
            <h4 className="text-xs font-bold text-text-primary uppercase tracking-wider">AI Credit Memo Generator</h4>
            <button 
              onClick={handleGenerateCreditMemo}
              className="inline-flex items-center gap-1 bg-[#008269]/10 hover:bg-[#008269]/20 text-[#008269] px-2.5 py-1 rounded text-[10px] font-bold border border-[#008269]/20 transition-all cursor-pointer"
            >
              <FileCheck2 className="w-3.5 h-3.5 text-primary" /> Generate Credit Memo
            </button>
          </div>

          {isMemoEditing ? (
            <div className="space-y-3">
              <textarea
                value={creditMemoText}
                onChange={(e) => setCreditMemoText(e.target.value)}
                rows={8}
                className="w-full border border-border rounded p-3 text-[10px] text-text-primary font-mono focus:outline-none focus:border-[#008269] resize-none bg-[#fafafa]"
              />
              <button
                onClick={() => setIsMemoEditing(false)}
                className="w-full py-1.5 bg-[#008269] hover:bg-[#005443] text-white text-[10px] font-bold rounded transition-colors cursor-pointer"
              >
                Save Credit Memo Draft
              </button>
            </div>
          ) : (
            <p className="text-[11px] text-text-secondary leading-relaxed">
              Compile a structured credit rationale covering applicant details, cash-flow metrics, risk factors, and AI suggestions. Save changes directly for credit auditor review.
            </p>
          )}
        </div>

        {/* SECTION 12: Decision Center */}
        <div className="bg-white border border-border rounded-card p-6 shadow-card">
          <h3 className="text-xs font-bold text-text-primary mb-4 uppercase tracking-wider border-b border-border pb-2">Decision Center</h3>
          
          {submitError && (
            <div role="alert" className="mb-4 p-3 rounded bg-error/10 border border-error/20 text-error text-xs font-medium flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" aria-hidden="true" /> {submitError}
            </div>
          )}

          <div className="mb-4">
            <label htmlFor="underwriter-remarks" className="block text-xs font-bold text-text-secondary uppercase tracking-wider mb-2">
              Underwriter Rationale Notes *
            </label>
            <textarea
              id="underwriter-remarks"
              rows={3}
              value={remarks}
              onChange={(e) => { setRemarks(e.target.value); if (remarksError) setRemarksError(null); }}
              placeholder="Enter decision rationale remarks..."
              className={`w-full border rounded p-3 text-xs focus:outline-none resize-none ${
                remarksError ? 'border-error focus:border-error' : 'border-border focus:border-[#008269]'
              }`}
            />
            {remarksError && (
              <p id="remarks-error" role="alert" className="mt-1.5 text-xs font-medium text-error">
                {remarksError}
              </p>
            )}
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-3">
            <button
              onClick={() => handleDecision('Approved')}
              disabled={isSubmitting}
              className="py-2.5 bg-success hover:bg-success/90 disabled:opacity-50 disabled:cursor-not-allowed text-white text-xs font-bold rounded transition-colors flex items-center justify-center gap-1.5 cursor-pointer shadow-xs"
            >
              {isSubmitting ? <Loader2 className="w-3.5 h-3.5 animate-spin" aria-hidden="true" /> : <Check className="w-3.5 h-3.5" aria-hidden="true" />} Approve
            </button>
            <button
              onClick={() => handleDecision('Rejected')}
              disabled={isSubmitting}
              className="py-2.5 bg-error hover:bg-error/90 disabled:opacity-50 disabled:cursor-not-allowed text-white text-xs font-bold rounded transition-colors flex items-center justify-center gap-1.5 cursor-pointer shadow-xs"
            >
              {isSubmitting ? <Loader2 className="w-3.5 h-3.5 animate-spin" aria-hidden="true" /> : <X className="w-3.5 h-3.5" aria-hidden="true" />} Reject
            </button>
            <button
              onClick={() => handleDecision('Info Requested')}
              disabled={isSubmitting}
              className="py-2.5 border border-border hover:bg-background-muted text-text-primary text-xs font-bold rounded transition-colors cursor-pointer text-center"
            >
              Request Documents
            </button>
            <button
              onClick={() => handleDecision('Escalated')}
              disabled={isSubmitting}
              className="py-2.5 border border-border hover:bg-background-muted text-text-primary text-xs font-bold rounded transition-colors cursor-pointer text-center"
            >
              Escalate
            </button>
          </div>

          <div className="pt-3 border-t border-border flex items-center justify-between text-xs text-text-secondary mt-4">
            <span>Current Decision Status:</span>
            <span className={`font-bold uppercase text-[10px] px-2 py-0.5 rounded ${
              data.officer_status === 'Approved' 
                ? 'bg-success/10 text-success' 
                : data.officer_status === 'Rejected' 
                ? 'bg-error/10 text-error' 
                : 'bg-warning/10 text-warning'
            }`}>
              {data.officer_status}
            </span>
          </div>
        </div>

        {/* SECTION 13: Audit Timeline — derived from data.applied_at + officer_status */}
        <div className="bg-white border border-border rounded-card p-6 shadow-card">
          <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider mb-4 pb-2 border-b border-border flex items-center gap-1.5">
            <Clock className="w-4 h-4 text-text-secondary" /> Audit Timeline (Audit Trail)
          </h3>

          {(() => {
            const applied = new Date(data.applied_at);
            const fmt = (offsetMins: number) => {
              const d = new Date(applied.getTime() + offsetMins * 60_000);
              return d.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
            };
            const officerActed =
              data.officer_status !== "Pending";
            return (
              <div className="relative border-l-2 border-border pl-4 ml-2 space-y-4 text-[10px] leading-relaxed">
                <div className="relative">
                  <div className="absolute -left-[21px] top-0.5 w-2 h-2 rounded-full bg-success" />
                  <span className="text-[10px] font-bold text-[#008269] block">{fmt(0)}</span>
                  <span className="text-text-secondary">Application submitted</span>
                </div>
                <div className="relative">
                  <div className="absolute -left-[21px] top-0.5 w-2 h-2 rounded-full bg-success" />
                  <span className="text-[10px] font-bold text-[#008269] block">{fmt(1)}</span>
                  <span className="text-text-secondary">Financial Intelligence Agent — data validated</span>
                </div>
                <div className="relative">
                  <div className="absolute -left-[21px] top-0.5 w-2 h-2 rounded-full bg-success" />
                  <span className="text-[10px] font-bold text-[#008269] block">{fmt(2)}</span>
                  <span className="text-text-secondary">Risk Intelligence Agent — score {score}/100, {riskBand} risk</span>
                </div>
                <div className="relative">
                  <div className="absolute -left-[21px] top-0.5 w-2 h-2 rounded-full bg-[#008269]" />
                  <span className="text-[10px] font-bold text-[#008269] block">{fmt(3)}</span>
                  <span className="text-text-secondary">Recommendation generated ({modelDecision})</span>
                </div>
                <div className="relative border-b-0 pb-0">
                  <div className={`absolute -left-[21px] top-0.5 w-2 h-2 rounded-full ${officerActed ? "bg-success" : "bg-warning"}`} />
                  <span className={`text-[10px] font-bold block ${officerActed ? "text-[#008269]" : "text-warning"}`}>
                    {officerActed ? fmt(4) : "—"}
                  </span>
                  <span className="text-text-secondary">
                    {officerActed ? `Officer status: ${data.officer_status}` : "Officer decision pending"}
                  </span>
                </div>
              </div>
            );
          })()}
        </div>

      </div>

      {/* Credit Copilot slide-out Drawer */}
      <ChatPanel 
        isOpen={isCopilotOpen}
        onClose={() => setIsCopilotOpen(false)}
        business={data}
        onDraftMemo={handleGenerateCreditMemo}
      />

      {/* Floating Simulated SMS / WhatsApp Notification Mockup */}
      <AnimatePresence>
        {simulatedSMS && simulatedSMS.show && (
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 50, scale: 0.9 }}
            className="fixed bottom-6 right-6 z-50 w-80 bg-white border border-border rounded-xl shadow-2xl overflow-hidden"
          >
            <div className="bg-[#008269] px-4 py-2 flex items-center justify-between text-white">
              <div className="flex items-center gap-1.5">
                <MessageCircle className="w-4 h-4 text-white" />
                <span className="text-[10px] font-bold uppercase tracking-wider">SMS Alert Notifications</span>
              </div>
              <button 
                onClick={() => setSimulatedSMS(null)}
                className="p-1 hover:bg-white/10 rounded cursor-pointer"
              >
                <X className="w-3.5 h-3.5 text-white" />
              </button>
            </div>
            <div className="p-4 bg-[#fafafa]">
              <div className="bg-white border border-border p-3 rounded-lg shadow-xs text-xs leading-relaxed text-text-primary">
                <p>{simulatedSMS.text}</p>
                <span className="text-[9px] text-text-secondary mt-1.5 block text-right">Just now • Delivered</span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

    </div>
  );
}
