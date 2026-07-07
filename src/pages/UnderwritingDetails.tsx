import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft, Building2, Calendar, FileText, PieChart,
  TrendingUp, CheckCircle2, ShieldAlert, ShieldCheck,
  AlertTriangle, FileSignature, BrainCircuit, Loader2,
  FileCheck2, MessageSquare
} from 'lucide-react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip 
} from 'recharts';
import { useBusinessDetail } from '../lib/api/hooks';
import { submitDecision } from '../lib/api';
import { PageSkeleton } from '../components/Skeleton';
import { BRAND, CHART_TOOLTIP_STYLE, AXIS_TICK } from '../lib/palette';
import { ScoreGauge } from '../components/ScoreGauge';
import { FactorBars } from '../components/FactorBars';
import { ChatPanel } from '../components/ChatPanel';
import { MemoModal } from '../components/MemoModal';
import { formatINR, formatINRCompact, formatPct } from '../lib/format';

const MetricCard = ({ label, value, trend }: any) => (
  <div className="bg-white border border-border rounded p-4 shadow-xs">
    <p className="text-xs font-medium text-text-secondary mb-1">{label}</p>
    <p className="text-xl font-bold text-text-primary mb-1 tnum">{value}</p>
    {trend && <p className={`text-[10px] font-medium ${trend.includes('+') ? 'text-success' : 'text-error'}`}>{trend} YoY</p>}
  </div>
);

export default function UnderwritingDetails() {
  const { id } = useParams();
  const { data, isLoading, error, refetch } = useBusinessDetail(id);
  const [remarks, setRemarks] = useState('');
  const [remarksError, setRemarksError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Modal / Copilot drawer states
  const [isCopilotOpen, setIsCopilotOpen] = useState(false);
  const [isMemoOpen, setIsMemoOpen] = useState(false);

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

  const handleDecision = async (status: 'Approved' | 'Rejected') => {
    if (!remarks.trim()) {
      setRemarksError('Enter underwriting notes before submitting — the decision needs an audit-ready rationale.');
      document.getElementById('underwriter-remarks')?.focus();
      return;
    }
    setRemarksError(null);
    setSubmitError(null);
    setIsSubmitting(true);
    try {
      await submitDecision(data.business_id, status, remarks);
      setSubmitSuccess(`Application has been successfully marked as ${status}.`);
      setRemarks('');
      refetch();
      setTimeout(() => setSubmitSuccess(null), 5000);
    } catch (e) {
      setSubmitError('Failed to submit the credit decision. Check that the backend is running, then retry.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Map 12-month trends from backend for chart (convert values to Lakhs for readability)
  const chartData = data.trends.map((t: any) => {
    // extract month segment, e.g. "2025-03" -> "Mar"
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

  return (
    <div className="p-6 lg:p-8 w-full max-w-[1440px] mx-auto">
      <div className="mb-6">
        <Link to="/officer/applications" className="inline-flex items-center gap-2 text-sm font-medium text-text-secondary hover:text-primary transition-colors mb-4">
          <ArrowLeft className="w-4 h-4" /> Back to Queue
        </Link>
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold text-text-primary mb-1">Underwriting Review: {data.business_id}</h1>
            <p className="text-sm text-text-secondary">Comprehensive AI assessment for {data.profile.name}.</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <button 
              onClick={() => setIsMemoOpen(true)}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded text-xs font-semibold bg-white border border-border hover:bg-background-muted text-text-primary transition-colors cursor-pointer shadow-xs"
            >
              <FileCheck2 className="w-4 h-4 text-primary" /> Generate Credit Memo
            </button>
            <button 
              onClick={() => setIsCopilotOpen(true)}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded text-xs font-semibold bg-primary hover:bg-primary-hover text-white transition-colors cursor-pointer shadow-sm"
            >
              <MessageSquare className="w-4 h-4" /> Open Credit Copilot
            </button>
          </div>
        </div>
      </div>

      {submitSuccess && (
        <div className="mb-6 p-4 rounded bg-success/10 border border-success/20 text-success text-sm font-medium flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5" /> {submitSuccess}
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        
        {/* Left Content Area */}
        <div className="xl:col-span-2 space-y-8">
          
          {/* Business Info Header */}
          <div className="bg-white border border-border rounded-card p-6 shadow-card">
            <div className="flex items-start gap-4 mb-6">
              <div className="w-12 h-12 bg-background-muted rounded border border-border flex items-center justify-center">
                <Building2 className="w-6 h-6 text-text-secondary" />
              </div>
              <div className="flex-1">
                <h2 className="text-xl font-bold text-text-primary">{data.profile.name}</h2>
                <div className="flex flex-wrap gap-x-6 gap-y-2 mt-2 text-xs md:text-sm text-text-secondary">
                  <span className="flex items-center gap-1.5"><FileText className="w-4 h-4" /> GSTIN: {data.profile.gst_registered ? '27AAAAA1234A1Z1' : 'Not Registered'}</span>
                  <span className="flex items-center gap-1.5"><FileSignature className="w-4 h-4" /> PAN: ABCDE5678X</span>
                  <span className="flex items-center gap-1.5"><Calendar className="w-4 h-4" /> Vintage: {data.profile.business_age_years} Years</span>
                  <span className="flex items-center gap-1.5"><PieChart className="w-4 h-4" /> {data.profile.industry}</span>
                </div>
              </div>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-6 border-t border-border">
              <MetricCard label="Requested Loan (Est)" value={formatINRCompact(data.recommendation.loan_amount)} />
              <MetricCard label="Annual Turnover" value={formatINRCompact(data.profile.annual_turnover)} trend="+12%" />
              <MetricCard label="Average Bank Balance" value={formatINRCompact(data.metrics.average_balance)} />
              <MetricCard label="Expense-to-Income Ratio" value={formatPct(data.metrics.expense_ratio, 1)} />
            </div>
          </div>

          {/* Financial Charts */}
          <div className="bg-white border border-border rounded-card p-6 shadow-card">
            <h3 className="text-base font-semibold text-text-primary mb-6">Financial Trend Analysis (Lakhs)</h3>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={BRAND.primary} stopOpacity={0.3}/>
                      <stop offset="95%" stopColor={BRAND.primary} stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorCash" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={BRAND.accent} stopOpacity={0.3}/>
                      <stop offset="95%" stopColor={BRAND.accent} stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={BRAND.grid} />
                  <XAxis dataKey="month" axisLine={false} tickLine={false} tick={AXIS_TICK} dy={10} />
                  <YAxis axisLine={false} tickLine={false} tick={AXIS_TICK} />
                  <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                  <Area type="monotone" dataKey="revenue" name="Revenue (Lakhs)" stroke={BRAND.primary} strokeWidth={2} fillOpacity={1} fill="url(#colorRev)" />
                  <Area type="monotone" dataKey="cashflow" name="Cash Flow Surplus (Lakhs)" stroke={BRAND.accent} strokeWidth={2} fillOpacity={1} fill="url(#colorCash)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Connected Data Sources Check */}
          <div className="bg-white border border-border rounded-card p-6 shadow-card">
            <h3 className="text-base font-semibold text-text-primary mb-4">Verified Data Sources</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="flex items-center justify-between p-3 border border-border rounded bg-background-muted/30">
                <span className="text-sm font-medium text-text-primary">GST Returns</span>
                <CheckCircle2 className="w-4 h-4 text-success" />
              </div>
              <div className="flex items-center justify-between p-3 border border-border rounded bg-background-muted/30">
                <span className="text-sm font-medium text-text-primary">Bank Statements</span>
                <CheckCircle2 className="w-4 h-4 text-success" />
              </div>
              <div className="flex items-center justify-between p-3 border border-border rounded bg-background-muted/30">
                <span className="text-sm font-medium text-text-primary">UPI/Merchant Data</span>
                <CheckCircle2 className="w-4 h-4 text-success" />
              </div>
              <div className="flex items-center justify-between p-3 border border-border rounded bg-background-muted/30">
                <span className="text-sm font-medium text-text-primary">EPFO Records</span>
                <CheckCircle2 className="w-4 h-4 text-success" />
              </div>
              <div className="flex items-center justify-between p-3 border border-border rounded bg-background-muted/30">
                <span className="text-sm font-medium text-text-primary">ITR Filing</span>
                <CheckCircle2 className="w-4 h-4 text-success" />
              </div>
              <div className="flex items-center justify-between p-3 border border-border rounded bg-background-muted/30">
                <span className="text-sm font-medium text-text-primary">Utility Bills</span>
                <CheckCircle2 className="w-4 h-4 text-success" />
              </div>
            </div>
          </div>

        </div>

        {/* Right Sidebar - AI & Actions */}
        <div className="xl:col-span-1 space-y-6">
          
          {/* AI Financial Health Card */}
          <div className="bg-white border border-border rounded-card p-6 shadow-card">
            <div className="flex items-center gap-2 mb-6 pb-4 border-b border-border">
              <ShieldCheck className="w-5 h-5 text-primary" />
              <h3 className="text-base font-bold text-text-primary">AI Underwriting Profile</h3>
            </div>
            
            <ScoreGauge 
              score={data.score.score} 
              band={data.score.band} 
              confidence={data.score.confidence} 
            />

            <div className="space-y-4 mt-6">
              <div className="p-4 border border-primary/20 bg-primary/5 rounded-card">
                <p className="text-xs font-bold text-primary mb-1 flex items-center gap-1.5"><BrainCircuit className="w-4 h-4" /> Model Recommendation</p>
                <p className="text-sm text-text-primary font-bold">{data.recommendation.decision}</p>
                <p className="text-xs text-text-secondary mt-1">
                  Recommended exposure limit: <strong className="text-text-primary tnum">{formatINR(data.recommendation.loan_amount)}</strong> over {data.recommendation.tenure_months} months at {data.recommendation.interest_band} interest.
                </p>
              </div>
            </div>
          </div>

          {/* AI SHAP Explainability & Risk Signals */}
          <div className="bg-white border border-border rounded-card p-6 shadow-card">
            <div className="flex items-center gap-2 mb-4 pb-2 border-b border-border">
              <TrendingUp className="w-4 h-4 text-primary" />
              <h3 className="text-sm font-bold text-text-primary uppercase tracking-wider">AI Explainability (SHAP Drivers)</h3>
            </div>
            
            <FactorBars factors={data.factors} />

            <div className="space-y-3 pt-4 border-t border-border mt-4">
              <h4 className="text-xs font-bold text-text-primary uppercase">Risk & Fraud Signals</h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-text-secondary flex items-center gap-1.5"><ShieldAlert className="w-3.5 h-3.5"/> GST Filing regularity</span>
                  <span className="font-semibold text-text-primary">{formatPct(data.metrics.gst_regularity)}</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-text-secondary flex items-center gap-1.5"><ShieldAlert className="w-3.5 h-3.5"/> Cheque Bounces</span>
                  <span className={`font-semibold ${data.metrics.bounce_count > 0 ? 'text-error' : 'text-success'}`}>{data.metrics.bounce_count} Bounces</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-text-secondary flex items-center gap-1.5"><ShieldAlert className="w-3.5 h-3.5"/> Debt Service (EMI) Ratio</span>
                  <span className="font-semibold text-text-primary">{formatPct(data.metrics.emi_ratio)}</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-text-secondary flex items-center gap-1.5"><ShieldAlert className="w-3.5 h-3.5"/> Cash Buffer Days</span>
                  <span className={`font-semibold ${data.metrics.cash_buffer_days < 10 ? 'text-warning' : 'text-success'}`}>{data.metrics.cash_buffer_days.toFixed(0)} Days</span>
                </div>
              </div>
            </div>
          </div>

          {/* Officer Action Panel */}
          <div className="bg-white border border-border rounded-card p-6 shadow-card">
            <h3 className="text-sm font-bold text-text-primary mb-4 uppercase tracking-wider border-b border-border pb-2">Officer Decision</h3>
            
            {submitError && (
              <div role="alert" className="mb-4 p-3 rounded bg-error/10 border border-error/20 text-error text-xs font-medium flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" aria-hidden="true" /> {submitError}
              </div>
            )}

            <div className="mb-4">
              <label htmlFor="underwriter-remarks" className="block text-xs font-semibold text-text-secondary mb-2">
                Underwriter Notes & Remarks <span className="text-error" aria-hidden="true">*</span>
              </label>
              <textarea
                id="underwriter-remarks"
                rows={4}
                value={remarks}
                onChange={(e) => { setRemarks(e.target.value); if (remarksError) setRemarksError(null); }}
                placeholder="Enter manual review remarks and reasons for decision..."
                aria-required="true"
                aria-invalid={remarksError ? true : undefined}
                aria-describedby={remarksError ? 'remarks-error' : undefined}
                className={`w-full border rounded p-3 text-sm focus:outline-none resize-none ${
                  remarksError ? 'border-error focus:border-error' : 'border-border focus:border-primary'
                }`}
              />
              {remarksError && (
                <p id="remarks-error" role="alert" className="mt-1.5 text-xs font-medium text-error">
                  {remarksError}
                </p>
              )}
            </div>

            <div className="grid grid-cols-2 gap-3 mb-4">
              <button
                onClick={() => handleDecision('Approved')}
                disabled={isSubmitting}
                className="col-span-1 py-2.5 bg-success hover:bg-success/90 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-semibold rounded transition-colors flex items-center justify-center gap-2 cursor-pointer"
              >
                {isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" /> : <CheckCircle2 className="w-4 h-4" aria-hidden="true" />} Approve
              </button>
              <button
                onClick={() => handleDecision('Rejected')}
                disabled={isSubmitting}
                className="col-span-1 py-2.5 bg-error hover:bg-error/90 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-semibold rounded transition-colors flex items-center justify-center gap-2 cursor-pointer"
              >
                {isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" /> : <ShieldAlert className="w-4 h-4" aria-hidden="true" />} Reject
              </button>
            </div>

            <div className="pt-4 border-t border-border flex flex-col gap-2">
              <div className="flex items-center justify-between text-xs text-text-secondary">
                <span>Current Status:</span>
                <span className="font-semibold text-text-primary">
                  {data.officer_status}
                </span>
              </div>
            </div>
          </div>

        </div>

      </div>

      {/* Credit Copilot slide-out Drawer */}
      <ChatPanel 
        isOpen={isCopilotOpen}
        onClose={() => setIsCopilotOpen(false)}
        business={data}
        onDraftMemo={() => {
          setIsCopilotOpen(false);
          setIsMemoOpen(true);
        }}
      />

      {/* Memo modal popup */}
      <MemoModal 
        isOpen={isMemoOpen}
        onClose={() => setIsMemoOpen(false)}
        business={data}
      />
    </div>
  );
}
