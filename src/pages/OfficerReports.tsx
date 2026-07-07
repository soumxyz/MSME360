import React from 'react';
import {
  FileText,
  CheckCircle2,
  Clock,
  AlertTriangle
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';
import { usePortfolio } from '../lib/api/hooks';
import type { PortfolioRow } from '../lib/api/types';
import { PageSkeleton } from '../components/Skeleton';
import { BRAND, CHART_SERIES, CHART_TOOLTIP_STYLE, AXIS_TICK } from '../lib/palette';

const SummaryCard = ({ title, value, icon, colorClass }: any) => (
  <div className="bg-white border border-border rounded-card p-5 shadow-sm flex items-center justify-between">
    <div>
      <p className="text-xs font-medium text-text-secondary mb-1">{title}</p>
      <h3 className="text-2xl font-bold text-text-primary tnum">{value}</h3>
    </div>
    <div className={`p-3 rounded ${colorClass}`}>
      {icon}
    </div>
  </div>
);

export default function OfficerReports() {
  const { data, isLoading, error } = usePortfolio();
  const rows = (data || []) as PortfolioRow[];

  if (isLoading) return <PageSkeleton label="Loading underwriting analytics" />;
  if (error || !data) {
    return (
      <div className="p-6 text-center text-error">
        <p className="font-semibold">Error loading analytics</p>
        <p className="text-xs mt-1">Make sure the FastAPI server is running on port 8000.</p>
      </div>
    );
  }

  const total = rows.length;
  const approved = rows.filter((r) => r.officer_status === 'Approved' || r.officer_status === 'Conditional').length;
  const decided = rows.filter((r) => r.officer_status !== 'Pending').length;
  const pending = total - decided;
  const highRisk = rows.filter((r) => r.band === 'High').length;
  const approvalRate = decided > 0 ? Math.round((approved / decided) * 100) : 0;

  // Score distribution histogram (10-point buckets)
  const scoreBuckets = Array.from({ length: 10 }, (_, i) => ({
    name: `${i * 10}–${i * 10 + 9}`,
    count: rows.filter((r) => r.score >= i * 10 && r.score < i * 10 + 10).length,
  }));
  scoreBuckets[9].count += rows.filter((r) => r.score === 100).length;

  // Industry distribution (top 5 + Other)
  const indMap: Record<string, number> = {};
  rows.forEach((r) => { indMap[r.industry] = (indMap[r.industry] || 0) + 1; });
  const sorted = Object.entries(indMap).sort((a, b) => b[1] - a[1]);
  const industryData = sorted.slice(0, 5).map(([name, value]) => ({ name, value }));
  const otherCount = sorted.slice(5).reduce((acc, [, v]) => acc + v, 0);
  if (otherCount > 0) industryData.push({ name: 'Other', value: otherCount });

  return (
    <div className="p-6 lg:p-8 w-full max-w-[1440px] mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-text-primary mb-1">Underwriting Analytics</h1>
        <p className="text-sm text-text-secondary">Live platform metrics computed from the scored portfolio.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <SummaryCard
          title="Businesses Scored"
          value={total}
          icon={<FileText className="w-5 h-5" />}
          colorClass="bg-primary/10 text-primary"
        />
        <SummaryCard
          title="Approval Rate (of decided)"
          value={`${approvalRate}%`}
          icon={<CheckCircle2 className="w-5 h-5" />}
          colorClass="bg-success/10 text-success"
        />
        <SummaryCard
          title="Pending Reviews"
          value={pending}
          icon={<Clock className="w-5 h-5" />}
          colorClass="bg-warning/10 text-warning"
        />
        <SummaryCard
          title="High-Risk Businesses"
          value={highRisk}
          icon={<AlertTriangle className="w-5 h-5" />}
          colorClass="bg-error/10 text-error"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white border border-border rounded-card p-6 shadow-card">
          <h3 className="text-base font-semibold text-text-primary mb-1">Health Score Distribution</h3>
          <p className="text-xs text-text-secondary mb-6">Portfolio-wide model scores in 10-point bands</p>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={scoreBuckets} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={BRAND.grid} />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: BRAND.slate }} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={AXIS_TICK} />
                <Tooltip cursor={{ fill: BRAND.surfaceMuted }} contentStyle={CHART_TOOLTIP_STYLE} />
                <Bar dataKey="count" name="Businesses" fill={BRAND.primary} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white border border-border rounded-card p-6 shadow-card">
          <h3 className="text-base font-semibold text-text-primary mb-1">Industry Distribution</h3>
          <p className="text-xs text-text-secondary mb-6">Share of scored businesses by sector</p>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <RechartsPieChart>
                <Pie
                  data={industryData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {industryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={CHART_SERIES[index % CHART_SERIES.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                <Legend iconType="circle" wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
              </RechartsPieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
