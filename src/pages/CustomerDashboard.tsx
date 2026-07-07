import React from 'react';
import {
  Activity,
  ArrowRight,
  TrendingUp,
  BrainCircuit,
  AlertTriangle,
  CheckCircle2,
  Download,
  Banknote,
  ShieldCheck
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  Radar,
  Tooltip
} from 'recharts';
import { Link } from 'react-router-dom';
import { useBusinessDetail } from '../lib/api/hooks';
import { DEMO_BUSINESS_ID, gradeFromScore, categoryScores } from '../lib/customer';
import { formatINRCompact, formatMonth, formatPct } from '../lib/format';
import { PageSkeleton } from '../components/Skeleton';
import { BRAND, CHART_TOOLTIP_STYLE, AXIS_TICK } from '../lib/palette';

const SummaryCard = ({ title, value, icon, badge, badgeTone = 'success', trendLabel }: any) => (
  <div className="bg-white border border-border rounded-card p-5 shadow-card flex flex-col h-full">
    <div className="flex items-center justify-between mb-4">
      <h3 className="text-sm font-semibold text-text-secondary">{title}</h3>
      <div className="p-2 bg-background-muted rounded text-primary">
        {icon}
      </div>
    </div>
    <div className="mb-2">
      <span className="text-2xl font-bold text-text-primary tnum">{value}</span>
    </div>
    <div className="flex items-center gap-2 mt-auto">
      {badge && (
        <span className={`inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded border ${
          badgeTone === 'success' ? 'text-success bg-success/10 border-success/20' : 'text-warning bg-warning/10 border-warning/20'
        }`}>
          {badgeTone === 'success' ? <TrendingUp className="w-3 h-3" aria-hidden="true" /> : <AlertTriangle className="w-3 h-3" aria-hidden="true" />} {badge}
        </span>
      )}
      {trendLabel && <span className="text-xs text-text-secondary">{trendLabel}</span>}
    </div>
  </div>
);

export default function CustomerDashboard() {
  const { data, isLoading, error } = useBusinessDetail(DEMO_BUSINESS_ID);

  if (isLoading) return <PageSkeleton label="Loading your financial health overview" />;
  if (error || !data) {
    return (
      <div className="p-6 text-center text-error">
        <p className="font-semibold">Error loading your dashboard</p>
        <p className="text-xs mt-1">Make sure the FastAPI server is running on port 8000.</p>
      </div>
    );
  }

  const score = data.score.score;
  const positives = data.factors.filter((f) => f.direction === '+');
  const negatives = data.factors.filter((f) => f.direction === '-');
  const gstOnTimeMonths = Math.round(data.metrics.gst_regularity * 12);

  const barData = data.trends.slice(-6).map((t) => ({
    name: formatMonth(t.month),
    revenue: Math.round(t.revenue / 100000),
    expense: Math.round(t.expense / 100000),
  }));

  const radarData = categoryScores(data).map((c) => ({ subject: c.name, A: c.score, fullMark: 100 }));

  return (
    <div className="p-6 lg:p-8 w-full max-w-[1440px] mx-auto">
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary mb-1">Financial Health Overview</h1>
          <p className="text-sm text-text-secondary">AI analysis of {data.profile.name}, computed live from your connected data.</p>
        </div>
        <Link to="/customer/reports" className="bg-white border border-border hover:bg-background-muted text-text-primary px-4 py-2 rounded text-sm font-medium transition-colors flex items-center gap-2">
          <Download className="w-4 h-4" aria-hidden="true" /> View Report
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <SummaryCard
          title="Overall Health Score"
          value={`${score}/100`}
          icon={<Activity className="w-5 h-5" />}
          badge={`${data.score.band} Risk`}
          badgeTone={data.score.band === 'High' ? 'warning' : 'success'}
          trendLabel="Live model output"
        />
        <SummaryCard
          title="Eligible Loan Amount"
          value={formatINRCompact(data.recommendation.loan_amount)}
          icon={<Banknote className="w-5 h-5" />}
          badge={data.recommendation.decision === 'Approve' ? 'Pre-qualified' : data.recommendation.decision}
          badgeTone={data.recommendation.decision === 'Reject' ? 'warning' : 'success'}
        />
        <SummaryCard
          title="Business Grade"
          value={gradeFromScore(score)}
          icon={<ShieldCheck className="w-5 h-5" />}
          trendLabel={`${data.profile.industry} sector`}
        />
        <SummaryCard
          title="GST Compliance"
          value={formatPct(data.metrics.gst_regularity)}
          icon={<CheckCircle2 className="w-5 h-5 text-success" />}
          badge={gstOnTimeMonths >= 11 ? 'Excellent' : 'Needs Attention'}
          badgeTone={gstOnTimeMonths >= 11 ? 'success' : 'warning'}
          trendLabel={`${gstOnTimeMonths}/12 months on time`}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2 bg-white border border-border rounded-card p-6 shadow-card">
          <h3 className="text-base font-semibold text-text-primary mb-6">Revenue vs Expense Trend (Last 6 Months, Lakhs)</h3>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={BRAND.grid} />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={AXIS_TICK} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={AXIS_TICK} />
                <Tooltip cursor={{ fill: BRAND.surfaceMuted }} contentStyle={CHART_TOOLTIP_STYLE} />
                <Bar dataKey="revenue" name="Revenue (Lakhs)" fill={BRAND.primary} radius={[4, 4, 0, 0]} />
                <Bar dataKey="expense" name="Expense (Lakhs)" fill={BRAND.accent} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="lg:col-span-1 bg-white border border-border rounded-card p-6 shadow-card flex flex-col">
          <h3 className="text-base font-semibold text-text-primary mb-2">Category Performance</h3>
          <div className="flex-grow min-h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                <PolarGrid stroke={BRAND.grid} />
                <PolarAngleAxis dataKey="subject" tick={{ fill: BRAND.slate, fontSize: 11 }} />
                <Radar name="Score" dataKey="A" stroke={BRAND.primary} fill={BRAND.primary} fillOpacity={0.2} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* AI Business Summary & Confidence */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2 bg-primary/5 border border-primary/20 rounded-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <BrainCircuit className="w-5 h-5 text-primary" aria-hidden="true" />
            <h3 className="text-base font-semibold text-text-primary">AI Business Summary</h3>
          </div>

          <div className="mb-6">
            <h4 className="text-sm font-semibold text-text-primary mb-2">Executive Summary</h4>
            <p className="text-sm text-text-secondary leading-relaxed">
              {data.profile.name} scores <strong className="text-text-primary tnum">{score}/100</strong> ({data.score.band} risk).
              The model recommendation is <strong className="text-text-primary">{data.recommendation.decision}</strong> with
              an eligible exposure of {formatINRCompact(data.recommendation.loan_amount)} over {data.recommendation.tenure_months} months.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <h4 className="text-sm font-semibold text-text-primary mb-2">Business Strengths</h4>
              <ul className="space-y-2">
                {(positives.length ? positives : data.factors.slice(0, 2)).slice(0, 3).map((f) => (
                  <li key={f.name} className="flex items-start gap-2 text-sm text-text-secondary">
                    <CheckCircle2 className="w-4 h-4 text-success mt-0.5 flex-shrink-0" aria-hidden="true" />
                    {f.detail}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-text-primary mb-2">Areas for Improvement</h4>
              <ul className="space-y-2">
                {negatives.length > 0 ? negatives.slice(0, 3).map((f) => (
                  <li key={f.name} className="flex items-start gap-2 text-sm text-text-secondary">
                    <AlertTriangle className="w-4 h-4 text-warning mt-0.5 flex-shrink-0" aria-hidden="true" />
                    {f.detail}
                  </li>
                )) : (
                  <li className="flex items-start gap-2 text-sm text-text-secondary">
                    <CheckCircle2 className="w-4 h-4 text-success mt-0.5 flex-shrink-0" aria-hidden="true" />
                    No negative score drivers detected in the current assessment.
                  </li>
                )}
              </ul>
            </div>
          </div>

          <div className="bg-white border border-border p-4 rounded">
            <h4 className="text-sm font-semibold text-text-primary mb-1">Top Score Driver</h4>
            <p className="text-sm text-text-secondary leading-relaxed">
              <strong className="text-text-primary">{data.factors[0].label}</strong> carries the largest weight
              ({formatPct(data.factors[0].weight)}) in your current score. {data.factors[0].detail}
            </p>
          </div>
        </div>

        <div className="lg:col-span-1 bg-white border border-border rounded-card p-6 shadow-card">
          <h3 className="text-base font-semibold text-text-primary mb-1">Assessment Confidence</h3>
          <p className="text-xs text-text-secondary mb-6">Model confidence on this assessment</p>

          <div className="flex items-center justify-center mb-8">
            <div className="w-32 h-32 rounded-full border-[10px] border-success/20 border-t-success flex items-center justify-center">
              <span className="text-3xl font-bold text-success tnum">{Math.round(data.score.confidence * 100)}%</span>
            </div>
          </div>

          <div className="space-y-3">
            <p className="text-xs font-semibold text-text-primary mb-2">Assessment generated using:</p>
            <div className="flex items-center gap-2 text-sm text-text-secondary">
              <CheckCircle2 className="w-4 h-4 text-success" aria-hidden="true" /> Bank Statements (12 months)
            </div>
            <div className="flex items-center gap-2 text-sm text-text-secondary">
              <CheckCircle2 className="w-4 h-4 text-success" aria-hidden="true" /> GST Filing Timeline
            </div>
            <div className="flex items-center gap-2 text-sm text-text-secondary">
              <CheckCircle2 className="w-4 h-4 text-success" aria-hidden="true" /> Cash Flow Metrics (20 engineered features)
            </div>
            <div className="flex items-center gap-2 text-sm text-text-secondary">
              <CheckCircle2 className="w-4 h-4 text-success" aria-hidden="true" /> SHAP Explainability Attributions
            </div>
          </div>
        </div>
      </div>

      {/* Next Step Section */}
      <div className="bg-white border border-border rounded-card p-8 shadow-card text-center mb-8">
        <h2 className="text-xl font-semibold text-text-primary mb-2">Next Step</h2>
        <p className="text-text-secondary mb-6 max-w-lg mx-auto">
          Based on your {score}/100 health score, you are eligible for credit facilities of up to {formatINRCompact(data.recommendation.loan_amount)}.
          Explore offers mapped to your operational profile.
        </p>
        <Link to="/customer/loans" className="inline-flex items-center gap-2 bg-primary hover:bg-primary-hover text-white px-8 py-3 rounded font-medium transition-colors">
          Explore Loan Offers <ArrowRight className="w-5 h-5" aria-hidden="true" />
        </Link>
      </div>

    </div>
  );
}
