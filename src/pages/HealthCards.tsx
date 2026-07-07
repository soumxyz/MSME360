import React, { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Search,
  Eye
} from 'lucide-react';
import { usePortfolio } from '../lib/api/hooks';
import type { PortfolioRow } from '../lib/api/types';
import { formatDate, formatPct } from '../lib/format';
import { gradeFromScore } from '../lib/customer';
import { PageSkeleton } from '../components/Skeleton';

const PAGE_SIZE = 10;

const RiskBadge = ({ risk }: { risk: string }) => {
  if (risk === 'Low') return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-success/10 text-success border border-success/20">Low Risk</span>;
  if (risk === 'Medium') return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-warning/10 text-warning border border-warning/20">Med Risk</span>;
  return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-error/10 text-error border border-error/20">High Risk</span>;
};

export default function HealthCards() {
  const { data, isLoading, error } = usePortfolio();
  const rows = (data || []) as PortfolioRow[];

  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);

  const filtered = useMemo(() => {
    const q = searchTerm.toLowerCase();
    return rows.filter((r) => r.name.toLowerCase().includes(q) || r.business_id.toLowerCase().includes(q));
  }, [rows, searchTerm]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const currentPage = Math.min(page, totalPages);
  const pageRows = filtered.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);

  if (isLoading) return <PageSkeleton label="Loading financial health cards" />;
  if (error || !data) {
    return (
      <div className="p-6 text-center text-error">
        <p className="font-semibold">Error loading health cards</p>
        <p className="text-xs mt-1">Make sure the FastAPI server is running on port 8000.</p>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 w-full max-w-[1440px] mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-text-primary mb-1">Financial Health Cards</h1>
        <p className="text-sm text-text-secondary">AI-generated financial health assessments for all {rows.length} scored businesses.</p>
      </div>

      <div className="bg-white border border-border rounded-card shadow-card overflow-hidden">
        <div className="p-5 border-b border-border">
          <div className="relative w-full sm:w-64">
            <Search className="w-4 h-4 text-text-secondary absolute left-3 top-1/2 -translate-y-1/2" aria-hidden="true" />
            <input
              type="search"
              placeholder="Search business..."
              aria-label="Search businesses"
              value={searchTerm}
              onChange={(e) => { setSearchTerm(e.target.value); setPage(1); }}
              className="pl-9 pr-4 py-2 border border-border rounded text-sm focus:outline-none focus:border-primary w-full"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-background-muted/30 border-b border-border">
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Business Name</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Health Score</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Business Grade</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Risk</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Model Confidence</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Generated Date</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {pageRows.map((card) => (
                <tr key={card.business_id} className="hover:bg-background-muted/30 transition-colors">
                  <td className="px-5 py-4">
                    <span className="text-sm font-semibold text-text-primary block">{card.name}</span>
                    <span className="text-[10px] text-text-secondary">{card.business_id} • {card.industry}</span>
                  </td>
                  <td className="px-5 py-4">
                    <span className={`text-sm font-bold tnum ${card.score >= 75 ? 'text-success' : card.score >= 55 ? 'text-warning' : 'text-error'}`}>
                      {card.score}
                    </span>
                  </td>
                  <td className="px-5 py-4 text-sm font-bold text-text-primary">{gradeFromScore(card.score)}</td>
                  <td className="px-5 py-4"><RiskBadge risk={card.band} /></td>
                  <td className="px-5 py-4 text-sm text-text-secondary tnum">{formatPct(card.confidence)}</td>
                  <td className="px-5 py-4 text-sm text-text-secondary">{formatDate(card.applied_at)}</td>
                  <td className="px-5 py-4 text-right">
                    <Link
                      to={`/officer/applications/${card.business_id}`}
                      aria-label={`Open health card for ${card.name}`}
                      className="inline-flex items-center justify-center w-8 h-8 rounded bg-primary/10 hover:bg-primary/20 text-primary transition-colors"
                      title="Open Card"
                    >
                      <Eye className="w-4 h-4" aria-hidden="true" />
                    </Link>
                  </td>
                </tr>
              ))}
              {pageRows.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-5 py-10 text-center text-sm text-text-secondary">
                    No businesses match the current search.
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
