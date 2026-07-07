import React from 'react';
import {
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle2,
  Lightbulb
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend
} from 'recharts';
import { useBusinessDetail } from '../lib/api/hooks';
import { DEMO_BUSINESS_ID } from '../lib/customer';
import { formatMonth, formatPct } from '../lib/format';
import { PageSkeleton } from '../components/Skeleton';
import { BRAND, CHART_SERIES, CHART_TOOLTIP_STYLE, AXIS_TICK } from '../lib/palette';

export default function BusinessInsights() {
  const { data, isLoading, error } = useBusinessDetail(DEMO_BUSINESS_ID);

  if (isLoading) return <PageSkeleton label="Loading business insights" />;
  if (error || !data) {
    return (
      <div className="p-6 text-center text-error">
        <p className="font-semibold">Error loading insights</p>
        <p className="text-xs mt-1">Make sure the FastAPI server is running on port 8000.</p>
      </div>
    );
  }

  const revenueTrend = data.trends.map((t) => ({
    month: formatMonth(t.month),
    surplus: Math.round((t.revenue - t.expense) / 100000),
  }));
  const lastSurplus = revenueTrend[revenueTrend.length - 1]?.surplus ?? 0;
  const firstSurplus = revenueTrend[0]?.surplus ?? 0;
  const improving = lastSurplus >= firstSurplus;

  // SHAP factor weights drive the category breakdown — these are the real score drivers
  const factorDistribution = data.factors.map((f) => ({
    name: f.label,
    value: Math.round(f.weight * 100),
  }));

  const topNegative = data.factors.find((f) => f.direction === '-');
  const topPositive = data.factors.find((f) => f.direction === '+') ?? data.factors[0];

  return (
    <div className="p-6 lg:p-8 w-full max-w-[1440px] mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-text-primary mb-1">Business Insights</h1>
        <p className="text-sm text-text-secondary">The factors driving the {data.score.score}/100 financial health score of {data.profile.name}, explained by SHAP attribution.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="md:col-span-2 bg-white border border-border rounded-card p-6 shadow-card">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-base font-semibold text-text-primary">Monthly Cash Surplus (Lakhs)</h3>
              <p className="text-xs text-text-secondary">Revenue minus expenses over the last 12 months</p>
            </div>
            <div className={`flex items-center gap-2 px-3 py-1 rounded text-sm font-medium ${improving ? 'bg-success/10 text-success' : 'bg-warning/10 text-warning'}`}>
              {improving ? <TrendingUp className="w-4 h-4" aria-hidden="true" /> : <TrendingDown className="w-4 h-4" aria-hidden="true" />}
              {improving ? 'Stable / Improving' : 'Softening'}
            </div>
          </div>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={revenueTrend} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorHealth" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={BRAND.primary} stopOpacity={0.2}/>
                    <stop offset="95%" stopColor={BRAND.primary} stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={BRAND.grid} />
                <XAxis dataKey="month" axisLine={false} tickLine={false} tick={AXIS_TICK} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={AXIS_TICK} />
                <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                <Area type="monotone" dataKey="surplus" name="Surplus (Lakhs)" stroke={BRAND.primary} strokeWidth={3} fillOpacity={1} fill="url(#colorHealth)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white border border-border rounded-card p-6 shadow-card">
          <h3 className="text-base font-semibold text-text-primary mb-2">Score Driver Breakdown</h3>
          <p className="text-xs text-text-secondary mb-4">SHAP weight of the top 5 factors</p>
          <div className="h-[220px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={factorDistribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {factorDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={CHART_SERIES[index % CHART_SERIES.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                <Legend iconType="circle" wrapperStyle={{ fontSize: '11px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white border border-border rounded-card shadow-card overflow-hidden">
          <div className="p-5 border-b border-border bg-background-muted/30">
            <h3 className="text-base font-semibold text-text-primary">Key Score Drivers</h3>
            <p className="text-xs text-text-secondary mt-0.5">Ranked by SHAP attribution weight from the live scoring model</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-border bg-white">
                  <th className="px-5 py-3 text-xs font-medium text-text-secondary uppercase tracking-wider">Factor</th>
                  <th className="px-5 py-3 text-xs font-medium text-text-secondary uppercase tracking-wider">Weight</th>
                  <th className="px-5 py-3 text-xs font-medium text-text-secondary uppercase tracking-wider">Impact</th>
                  <th className="px-5 py-3 text-xs font-medium text-text-secondary uppercase tracking-wider">What the model observed</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {data.factors.map((f) => (
                  <tr key={f.name} className="hover:bg-background-muted/50 transition-colors">
                    <td className="px-5 py-4 text-sm font-medium text-text-primary">{f.label}</td>
                    <td className="px-5 py-4 text-sm text-text-primary tnum">{formatPct(f.weight)}</td>
                    <td className="px-5 py-4">
                      {f.direction === '+' ? (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-medium bg-success/10 text-success">
                          <TrendingUp className="w-3 h-3" aria-hidden="true" /> Positive
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-medium bg-warning/10 text-warning">
                          <TrendingDown className="w-3 h-3" aria-hidden="true" /> Negative
                        </span>
                      )}
                    </td>
                    <td className="px-5 py-4 text-sm text-text-secondary">{f.detail}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="lg:col-span-1 bg-primary/5 border border-primary/20 rounded-card p-6 shadow-sm flex flex-col">
          <div className="flex items-center gap-2 mb-6 border-b border-primary/20 pb-4">
            <Lightbulb className="w-5 h-5 text-primary" aria-hidden="true" />
            <h3 className="text-base font-semibold text-text-primary">Insight Explanation Panel</h3>
          </div>
          <div className="flex-grow space-y-6">
            {topNegative ? (
              <div>
                <h4 className="text-sm font-bold text-text-primary mb-2 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-warning" aria-hidden="true" /> {topNegative.label}
                </h4>
                <p className="text-sm text-text-secondary leading-relaxed mb-3">
                  <strong className="text-text-primary block mb-1">Why AI flagged it:</strong>
                  {topNegative.detail} This factor carries {formatPct(topNegative.weight)} of the current attribution weight and pulls the score down.
                </p>
              </div>
            ) : (
              <div>
                <h4 className="text-sm font-bold text-text-primary mb-2 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-success" aria-hidden="true" /> No Negative Drivers
                </h4>
                <p className="text-sm text-text-secondary leading-relaxed">
                  All top score drivers currently contribute positively to your assessment.
                </p>
              </div>
            )}
            <div>
              <h4 className="text-sm font-bold text-text-primary mb-2 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-success" aria-hidden="true" /> Strongest Positive Signal
              </h4>
              <p className="text-sm text-text-secondary leading-relaxed">
                <strong className="text-text-primary">{topPositive.label}:</strong> {topPositive.detail} This
                is your most valuable signal — maintaining it protects {formatPct(topPositive.weight)} of your score attribution.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
