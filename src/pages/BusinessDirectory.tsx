import React, { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Search,
  Building2,
  ExternalLink
} from 'lucide-react';
import { usePortfolio } from '../lib/api/hooks';
import type { PortfolioRow } from '../lib/api/types';
import { formatINRCompact, formatDate } from '../lib/format';
import { PageSkeleton } from '../components/Skeleton';

const PAGE_SIZE = 10;

const RiskBadge = ({ risk }: { risk: string }) => {
  if (risk === 'Low') return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-success/10 text-success border border-success/20">Low Risk</span>;
  if (risk === 'Medium') return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-warning/10 text-warning border border-warning/20">Med Risk</span>;
  return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-error/10 text-error border border-error/20">High Risk</span>;
};

export default function BusinessDirectory() {
  const { data, isLoading, error } = usePortfolio();
  const rows = (data || []) as PortfolioRow[];

  const [searchTerm, setSearchTerm] = useState('');
  const [industryFilter, setIndustryFilter] = useState('');
  const [riskFilter, setRiskFilter] = useState('');
  const [page, setPage] = useState(1);

  const industries = useMemo(
    () => Array.from(new Set(rows.map((r) => r.industry))).sort(),
    [rows]
  );

  const filtered = useMemo(() => {
    const q = searchTerm.toLowerCase();
    return rows.filter((r) =>
      (r.name.toLowerCase().includes(q) || r.business_id.toLowerCase().includes(q)) &&
      (!industryFilter || r.industry === industryFilter) &&
      (!riskFilter || r.band === riskFilter)
    );
  }, [rows, searchTerm, industryFilter, riskFilter]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const currentPage = Math.min(page, totalPages);
  const pageRows = filtered.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);

  if (isLoading) return <PageSkeleton label="Loading business directory" />;
  if (error || !data) {
    return (
      <div className="p-6 text-center text-error">
        <p className="font-semibold">Error loading business directory</p>
        <p className="text-xs mt-1">Make sure the FastAPI server is running on port 8000.</p>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 w-full max-w-[1440px] mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-text-primary mb-1">Business Directory</h1>
        <p className="text-sm text-text-secondary">All {rows.length} MSME clients scored by the AI engine.</p>
      </div>

      <div className="bg-white border border-border rounded-card shadow-card overflow-hidden">
        <div className="p-5 border-b border-border flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-text-secondary absolute left-3 top-1/2 -translate-y-1/2" aria-hidden="true" />
            <input
              type="search"
              placeholder="Search business name or ID..."
              aria-label="Search business name or ID"
              value={searchTerm}
              onChange={(e) => { setSearchTerm(e.target.value); setPage(1); }}
              className="pl-9 pr-4 py-2 border border-border rounded text-sm focus:outline-none focus:border-primary w-full"
            />
          </div>
          <div className="flex gap-2">
            <select
              value={industryFilter}
              onChange={(e) => { setIndustryFilter(e.target.value); setPage(1); }}
              aria-label="Filter by industry"
              className="border border-border rounded px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-primary cursor-pointer bg-white"
            >
              <option value="">All Industries</option>
              {industries.map((ind) => <option key={ind} value={ind}>{ind}</option>)}
            </select>
            <select
              value={riskFilter}
              onChange={(e) => { setRiskFilter(e.target.value); setPage(1); }}
              aria-label="Filter by risk band"
              className="border border-border rounded px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-primary cursor-pointer bg-white"
            >
              <option value="">All Risks</option>
              <option value="Low">Low Risk</option>
              <option value="Medium">Medium Risk</option>
              <option value="High">High Risk</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-background-muted/30 border-b border-border">
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Business</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Industry</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Location</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Health Score</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Risk</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Est. Exposure</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Last Review</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {pageRows.map((biz) => (
                <tr key={biz.business_id} className="hover:bg-background-muted/30 transition-colors">
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded bg-background-muted border border-border flex items-center justify-center flex-shrink-0">
                        <Building2 className="w-4 h-4 text-text-secondary" aria-hidden="true" />
                      </div>
                      <div>
                        <span className="text-sm font-semibold text-text-primary block">{biz.name}</span>
                        <span className="text-[10px] text-text-secondary">{biz.business_id}</span>
                      </div>
                    </div>
                  </td>
                  <td className="px-5 py-4 text-sm text-text-secondary">{biz.industry}</td>
                  <td className="px-5 py-4 text-sm text-text-secondary">{biz.city}, {biz.state}</td>
                  <td className="px-5 py-4">
                    <span className={`text-sm font-bold tnum ${biz.score >= 75 ? 'text-success' : biz.score >= 55 ? 'text-warning' : 'text-error'}`}>
                      {biz.score}
                    </span>
                  </td>
                  <td className="px-5 py-4"><RiskBadge risk={biz.band} /></td>
                  <td className="px-5 py-4 text-sm font-semibold text-text-primary tnum">{formatINRCompact(biz.avg_monthly_revenue * 3)}</td>
                  <td className="px-5 py-4 text-sm text-text-secondary">{formatDate(biz.applied_at)}</td>
                  <td className="px-5 py-4 text-right">
                    <Link
                      to={`/officer/applications/${biz.business_id}`}
                      className="inline-flex items-center gap-1 px-3 py-1.5 bg-white border border-border hover:bg-background-muted text-text-secondary text-xs font-medium rounded transition-colors"
                    >
                      Open Card <ExternalLink className="w-3 h-3" aria-hidden="true" />
                    </Link>
                  </td>
                </tr>
              ))}
              {pageRows.length === 0 && (
                <tr>
                  <td colSpan={8} className="px-5 py-10 text-center text-sm text-text-secondary">
                    No businesses match the current search or filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="p-4 border-t border-border flex items-center justify-between text-sm text-text-secondary">
          <span className="tnum">
            Showing {filtered.length === 0 ? 0 : (currentPage - 1) * PAGE_SIZE + 1} to {Math.min(currentPage * PAGE_SIZE, filtered.length)} of {filtered.length} entries
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={currentPage <= 1}
              className="px-3 py-1 border border-border rounded hover:bg-background-muted disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
            >
              Prev
            </button>
            <span className="tnum text-xs">Page {currentPage} of {totalPages}</span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage >= totalPages}
              className="px-3 py-1 border border-border rounded hover:bg-background-muted disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
