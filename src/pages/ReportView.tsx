import React from 'react';
import {
  Activity,
  Printer,
  CheckCircle2,
  AlertTriangle,
  QrCode,
  ShieldCheck,
  ArrowLeft,
  ScrollText,
  FileText,
  Banknote,
  BrainCircuit
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  ResponsiveContainer,
  LabelList
} from 'recharts';
import { Link } from 'react-router-dom';
import { useBusinessDetail } from '../lib/api/hooks';
import { DEMO_BUSINESS_ID, gradeFromScore, categoryScores } from '../lib/customer';
import { formatINRCompact, formatPct } from '../lib/format';
import { PageSkeleton } from '../components/Skeleton';
import { BRAND, AXIS_TICK_SM } from '../lib/palette';
import type { BusinessDetail } from '../lib/api/types';

const ReportHeader = ({ businessId }: { businessId: string }) => (
  <div className="flex items-center justify-between border-b-2 border-primary pb-6 mb-8">
    <div className="flex items-center gap-3">
      <div className="w-10 h-10 bg-primary rounded flex items-center justify-center">
        <Activity className="w-6 h-6 text-white" aria-hidden="true" />
      </div>
      <div>
        <h1 className="text-xl font-bold text-primary tracking-tight uppercase">IDBI Bank</h1>
        <p className="text-[10px] text-text-secondary tracking-widest uppercase">MSME Assessment Portal</p>
      </div>
    </div>
    <div className="text-right">
      <h2 className="text-lg font-semibold text-text-primary">Financial Health Report</h2>
      <p className="text-xs text-text-secondary">Ref No: IDBI/FHR/{businessId}</p>
      <p className="text-xs text-text-secondary">Date: {new Date().toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}</p>
    </div>
  </div>
);

const SectionTitle = ({ title }: { title: string }) => (
  <h3 className="text-sm font-bold text-text-primary uppercase tracking-wider mb-4 border-b border-border pb-1">{title}</h3>
);

const BusinessInfo = ({ data }: { data: BusinessDetail }) => (
  <div className="mb-8">
    <SectionTitle title="Business Information" />
    <div className="grid grid-cols-2 gap-y-4 gap-x-8 text-sm">
      <div className="flex justify-between">
        <span className="text-text-secondary">Entity Name:</span>
        <span className="font-semibold text-text-primary">{data.profile.name}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-text-secondary">Business ID:</span>
        <span className="font-medium text-text-primary">{data.business_id}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-text-secondary">Industry:</span>
        <span className="font-medium text-text-primary">{data.profile.industry}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-text-secondary">Location:</span>
        <span className="font-medium text-text-primary">{data.profile.city}, {data.profile.state}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-text-secondary">Annual Turnover:</span>
        <span className="font-medium text-text-primary tnum">{formatINRCompact(data.profile.annual_turnover)}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-text-secondary">Assessment Confidence:</span>
        <span className="font-medium text-success tnum">{formatPct(data.score.confidence)}</span>
      </div>
    </div>
  </div>
);

const ScoresSection = ({ data }: { data: BusinessDetail }) => {
  const cats = categoryScores(data);
  return (
    <div className="mb-8">
      <SectionTitle title="Health Assessment Scores" />
      <div className="grid grid-cols-3 gap-6 mb-6">
        <div className="p-4 bg-background-muted border border-border rounded text-center">
          <p className="text-xs text-text-secondary mb-1">Final Health Score</p>
          <p className={`text-3xl font-bold tnum ${data.score.score >= 75 ? 'text-success' : data.score.score >= 55 ? 'text-warning' : 'text-error'}`}>
            {data.score.score}<span className="text-sm text-text-secondary font-normal">/100</span>
          </p>
        </div>
        <div className="p-4 bg-background-muted border border-border rounded text-center">
          <p className="text-xs text-text-secondary mb-1">Business Grade</p>
          <p className="text-3xl font-bold text-text-primary">{gradeFromScore(data.score.score)}</p>
        </div>
        <div className="p-4 bg-background-muted border border-border rounded text-center">
          <p className="text-xs text-text-secondary mb-1">Risk Band</p>
          <p className="text-xl font-bold text-text-primary mt-2">{data.score.band}</p>
        </div>
      </div>

      <div>
        <h4 className="text-xs font-semibold text-text-secondary mb-3">Category Breakdown (derived from model metrics)</h4>
        <div className="h-[180px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={cats} layout="vertical" margin={{ top: 0, right: 30, left: 0, bottom: 0 }}>
              <XAxis type="number" domain={[0, 100]} hide />
              <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={AXIS_TICK_SM} width={120} />
              <Bar dataKey="score" fill={BRAND.primary} radius={[0, 4, 4, 0]} barSize={16}>
                <LabelList dataKey="score" position="right" style={{ fontSize: '11px', fill: BRAND.ink, fontWeight: 600 }} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

const DataSourcesSection = () => (
  <div className="mb-8">
    <SectionTitle title="Assessment Inputs" />
    <div className="grid grid-cols-2 gap-y-3">
      <div className="flex items-center gap-2 text-sm text-text-secondary">
        <CheckCircle2 className="w-4 h-4 text-success" aria-hidden="true" /> <ScrollText className="w-3.5 h-3.5 opacity-50" aria-hidden="true" /> Bank Statements (12 months)
      </div>
      <div className="flex items-center gap-2 text-sm text-text-secondary">
        <CheckCircle2 className="w-4 h-4 text-success" aria-hidden="true" /> <FileText className="w-3.5 h-3.5 opacity-50" aria-hidden="true" /> GST Filing Timeline
      </div>
      <div className="flex items-center gap-2 text-sm text-text-secondary">
        <CheckCircle2 className="w-4 h-4 text-success" aria-hidden="true" /> <Activity className="w-3.5 h-3.5 opacity-50" aria-hidden="true" /> Engineered Cash Flow Metrics
      </div>
      <div className="flex items-center gap-2 text-sm text-text-secondary">
        <CheckCircle2 className="w-4 h-4 text-success" aria-hidden="true" /> <BrainCircuit className="w-3.5 h-3.5 opacity-50" aria-hidden="true" /> SHAP Attribution (Agent 2)
      </div>
    </div>
  </div>
);

const AIAnalysisSection = ({ data }: { data: BusinessDetail }) => {
  const positives = data.factors.filter((f) => f.direction === '+');
  const negatives = data.factors.filter((f) => f.direction === '-');
  return (
    <div className="mb-8">
      <SectionTitle title="AI Executive Summary" />
      <div className="space-y-4">
        <div className="border-l-2 border-primary pl-4">
          <p className="text-[11px] text-text-secondary leading-relaxed">
            {data.profile.name} scores {data.score.score}/100 ({data.score.band} risk) on the AI financial health assessment.
            The model recommendation is <strong>{data.recommendation.decision}</strong> with an eligible exposure
            of {formatINRCompact(data.recommendation.loan_amount)} over {data.recommendation.tenure_months} months
            at {data.recommendation.interest_band}.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-6 pt-2">
          <div>
            <h4 className="text-xs font-bold text-text-primary mb-2 flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-success" aria-hidden="true" /> Business Strengths
            </h4>
            <ul className="space-y-1 text-[11px] text-text-secondary list-disc pl-4">
              {(positives.length ? positives : data.factors.slice(0, 2)).slice(0, 3).map((f) => (
                <li key={f.name}>{f.detail}</li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-bold text-text-primary mb-2 flex items-center gap-1">
              <AlertTriangle className="w-3.5 h-3.5 text-warning" aria-hidden="true" /> Business Weaknesses
            </h4>
            <ul className="space-y-1 text-[11px] text-text-secondary list-disc pl-4">
              {negatives.length > 0 ? negatives.slice(0, 3).map((f) => (
                <li key={f.name}>{f.detail}</li>
              )) : (
                <li>No negative score drivers detected in the current top-5 attribution.</li>
              )}
            </ul>
          </div>
        </div>

        <div className="pt-2">
          <h4 className="text-xs font-bold text-text-primary mb-2 flex items-center gap-1">
            <Banknote className="w-3.5 h-3.5 text-success" aria-hidden="true" /> Eligible Loan Facility
          </h4>
          <ul className="space-y-2 text-[11px] text-text-secondary max-w-sm">
            <li className="flex justify-between border-b border-border pb-1">
              <span>Working Capital Loan</span>
              <span className="font-semibold text-text-primary tnum">{formatINRCompact(data.recommendation.loan_amount)}</span>
            </li>
            <li className="flex justify-between border-b border-border pb-1">
              <span>Tenure / Rate</span>
              <span className="font-semibold text-text-primary tnum">{data.recommendation.tenure_months} months @ {data.recommendation.interest_band}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

const ReportFooter = () => (
  <div className="mt-12 pt-6 border-t border-border flex justify-between items-end">
    <div className="flex gap-6">
      <div className="flex flex-col items-center">
        <QrCode className="w-16 h-16 text-text-primary mb-2" aria-hidden="true" />
        <span className="text-[9px] text-text-secondary">Scan to Verify</span>
      </div>
      <div className="flex flex-col justify-end">
        <p className="text-[10px] text-text-secondary max-w-xs leading-tight">
          This is an AI-generated report based on connected alternate data sources.
          Final credit decisions are subject to IDBI Bank's internal credit policy and manual underwriting verification.
        </p>
      </div>
    </div>
    <div className="text-right">
      <div className="w-32 h-12 mb-2 border-b border-text-secondary flex items-end justify-center pb-1">
        <span className="font-signature text-primary italic text-lg opacity-80">System Auth</span>
      </div>
      <p className="text-xs font-semibold text-text-primary flex items-center justify-end gap-1">
        <ShieldCheck className="w-3 h-3 text-success" aria-hidden="true" /> Digital Signature
      </p>
      <p className="text-[10px] text-text-secondary">MSME 360 AI Engine</p>
    </div>
  </div>
);

export default function ReportView() {
  const { data, isLoading, error } = useBusinessDetail(DEMO_BUSINESS_ID);

  if (isLoading) return <PageSkeleton label="Generating financial health report" />;
  if (error || !data) {
    return (
      <div className="p-6 text-center text-error">
        <p className="font-semibold">Error generating report</p>
        <p className="text-xs mt-1">Make sure the FastAPI server is running on port 8000.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background-muted font-sans selection:bg-primary selection:text-white pb-12 w-full">
      {/* Top Action Bar */}
      <div className="bg-white border-b border-border sticky top-0 z-50 mb-8 shadow-sm print:hidden">
        <div className="max-w-[1000px] mx-auto px-6 h-16 flex items-center justify-between">
          <Link to="/customer/dashboard" className="text-text-secondary hover:text-text-primary flex items-center gap-2 text-sm font-medium transition-colors">
            <ArrowLeft className="w-4 h-4" aria-hidden="true" /> Back to Dashboard
          </Link>
          <button
            onClick={() => window.print()}
            className="flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary-hover text-white rounded text-sm font-medium transition-colors cursor-pointer"
          >
            <Printer className="w-4 h-4" aria-hidden="true" /> Print / Save as PDF
          </button>
        </div>
      </div>

      {/* A4 Report Container */}
      <main className="max-w-[800px] mx-auto bg-white shadow-lg border border-border">
        <div className="p-12 md:p-16">
          <ReportHeader businessId={data.business_id} />
          <BusinessInfo data={data} />
          <DataSourcesSection />
          <ScoresSection data={data} />
          <AIAnalysisSection data={data} />
          <ReportFooter />
        </div>
      </main>
    </div>
  );
}
