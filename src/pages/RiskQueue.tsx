import React, { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Search,
  ArrowRight,
  ShieldCheck
} from 'lucide-react';
import { usePortfolio } from '../lib/api/hooks';
import type { PortfolioRow } from '../lib/api/types';
import { PageSkeleton } from '../components/Skeleton';

const SummaryCard = ({ title, value, colorClass }: { title: string, value: number, colorClass: string }) => (
  <div className="bg-white border border-border rounded-card p-5 shadow-sm flex items-center justify-between">
    <div>
      <p className="text-xs font-medium text-text-secondary mb-1">{title}</p>
      <h3 className="text-2xl font-bold text-text-primary tnum">{value}</h3>
    </div>
    <div className={`w-3 h-12 rounded-full ${colorClass}`}></div>
  </div>
);

const RiskBadge = ({ risk }: { risk: string }) => {
  if (risk === 'Critical') return <span className="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-bold bg-error text-white">CRITICAL</span>;
  if (risk === 'High') return <span className="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-bold bg-error/10 text-error border border-error/20">High</span>;
  if (risk === 'Medium') return <span className="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-bold bg-warning/10 text-warning border border-warning/20">Medium</span>;
  return <span className="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-bold bg-success/10 text-success border border-success/20">Low</span>;
};

/** Model-derived queue severity: sub-35 scores get flagged critical. */
const severityOf = (row: PortfolioRow) => (row.band === 'High' && row.score < 35 ? 'Critical' : row.band);

const reasonOf = (row: PortfolioRow) => {
  if (row.score < 35) return `Severely weak composite score (${row.score}/100) — immediate officer action advised`;
  if (row.band === 'High') return `High-risk score (${row.score}/100) flagged by the Agent 2 scoring model`;
  return `Medium-risk score (${row.score}/100) — periodic monitoring recommended`;
};

export default function RiskQueue() {
  const { data, isLoading, error } = usePortfolio();
  const rows = (data || []) as PortfolioRow[];
  const [searchTerm, setSearchTerm] = useState('');

  const criticalCount = rows.filter((r) => severityOf(r) === 'Critical').length;
  const highCount = rows.filter((r) => severityOf(r) === 'High').length;
  const mediumCount = rows.filter((r) => r.band === 'Medium').length;
  const lowCount = rows.filter((r) => r.band === 'Low').length;

  // Queue = everything not Low, worst score first
  const queue = useMemo(() => {
    const q = searchTerm.toLowerCase();
    return rows
      .filter((r) => r.band !== 'Low')
      .filter((r) => r.name.toLowerCase().includes(q) || r.business_id.toLowerCase().includes(q))
      .sort((a, b) => a.score - b.score)
      .slice(0, 25);
  }, [rows, searchTerm]);

  if (isLoading) return <PageSkeleton label="Loading risk queue" />;
  if (error || !data) {
    return (
      <div className="p-6 text-center text-error">
        <p className="font-semibold">Error loading risk queue</p>
        <p className="text-xs mt-1">Make sure the FastAPI server is running on port 8000.</p>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 w-full max-w-[1440px] mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-text-primary mb-1">Risk Queue</h1>
        <p className="text-sm text-text-secondary">Businesses requiring officer attention, prioritized by AI risk severity.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <SummaryCard title="Critical Alerts" value={criticalCount} colorClass="bg-error" />
        <SummaryCard title="High Risk" value={highCount} colorClass="bg-error/60" />
        <SummaryCard title="Medium Risk" value={mediumCount} colorClass="bg-warning" />
        <SummaryCard title="Low / Routine" value={lowCount} colorClass="bg-success" />
      </div>

      <div className="bg-white border border-border rounded-card shadow-card overflow-hidden">
        <div className="p-5 border-b border-border flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="relative">
            <Search className="w-4 h-4 text-text-secondary absolute left-3 top-1/2 -translate-y-1/2" aria-hidden="true" />
            <input
              type="search"
              placeholder="Search queue..."
              aria-label="Search risk queue"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9 pr-4 py-2 border border-border rounded text-sm focus:outline-none focus:border-primary w-full sm:w-64"
            />
          </div>
          <span className="text-sm text-text-secondary flex items-center gap-1">
            <ShieldCheck className="w-4 h-4 text-success" aria-hidden="true" /> Auto-sorted by severity — showing top {queue.length}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-background-muted/30 border-b border-border">
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Business</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Risk Level</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Health Score</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Reason</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Status</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {queue.map((item) => (
                <tr key={item.business_id} className="hover:bg-background-muted/30 transition-colors">
                  <td className="px-5 py-4">
                    <span className="text-sm font-semibold text-text-primary block">{item.name}</span>
                    <span className="text-[10px] text-text-secondary">{item.business_id} • {item.industry}</span>
                  </td>
                  <td className="px-5 py-4"><RiskBadge risk={severityOf(item)} /></td>
                  <td className="px-5 py-4 text-sm font-bold text-text-primary tnum">{item.score}/100</td>
                  <td className="px-5 py-4 text-sm text-text-secondary max-w-xs">{reasonOf(item)}</td>
                  <td className="px-5 py-4">
                    <span className={`text-xs font-medium ${item.officer_status === 'Pending' ? 'text-error' : 'text-text-secondary'}`}>
                      {item.officer_status === 'Pending' ? 'Action Required' : `Decided: ${item.officer_status}`}
                    </span>
                  </td>
                  <td className="px-5 py-4 text-right">
                    <Link
                      to={`/officer/applications/${item.business_id}`}
                      className="inline-flex items-center gap-1 px-3 py-1.5 bg-primary/10 hover:bg-primary/20 text-primary text-xs font-semibold rounded transition-colors"
                    >
                      Investigate <ArrowRight className="w-3 h-3" aria-hidden="true" />
                    </Link>
                  </td>
                </tr>
              ))}
              {queue.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-5 py-10 text-center text-sm text-text-secondary">
                    No businesses match the current search.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
