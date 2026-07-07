import React, { useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';

import {
  Search,
  FileText,
  Clock,
  BrainCircuit,
  CheckCircle2,
  AlertCircle,
  ArrowRight
} from 'lucide-react';
import { usePortfolio } from '../lib/api/hooks';
import type { PortfolioRow } from '../lib/api/types';
import { formatINRCompact } from '../lib/format';
import { PageSkeleton } from '../components/Skeleton';

const SummaryCard = ({ title, value, icon, colorClass }: any) => (
  <div className="bg-white border border-border rounded-card p-5 shadow-sm flex items-center justify-between">
    <div>
      <p className="text-xs font-medium text-text-secondary mb-1">{title}</p>
      <h3 className="text-2xl font-bold text-text-primary">{value}</h3>
    </div>
    <div className={`p-3 rounded ${colorClass}`}>
      {icon}
    </div>
  </div>
);

const StatusBadge = ({ status }: { status: string }) => {
  switch (status) {
    case 'Approved':
      return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-success/10 text-success border border-success/20">Approved</span>;
    case 'Rejected':
      return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-error/10 text-error border border-error/20">Rejected</span>;
    case 'Conditional':
      return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-secondary/10 text-secondary border border-secondary/20">Conditional</span>;
    case 'Pending':
      return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-warning/10 text-warning border border-warning/20">Pending</span>;
    default:
      return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-background-muted text-text-secondary border border-border">{status}</span>;
  }
};

const RiskBadge = ({ risk }: { risk: string }) => {
  if (risk === 'Low') return <span className="text-success font-semibold text-sm">Low</span>;
  if (risk === 'Medium') return <span className="text-warning font-semibold text-sm">Medium</span>;
  return <span className="text-error font-semibold text-sm">High</span>;
};

export default function OfficerApplications() {
  const { data, isLoading, error } = usePortfolio();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All Statuses');

  if (isLoading) {
    return <PageSkeleton label="Loading applications queue" />;
  }

  if (error || !data) {
    return (
      <div className="p-6 text-center text-error">
        <p className="font-semibold">Error loading applications</p>
        <p className="text-xs mt-1">Make sure the FastAPI server is running on port 8000.</p>
      </div>
    );
  }

  const portfolioRows = (data || []) as PortfolioRow[];

  // --- Dynamic Stats Computations ---
  const totalApps = portfolioRows.length;
  const pendingCount = portfolioRows.filter((r: PortfolioRow) => r.officer_status === 'Pending').length;
  const approvedCount = portfolioRows.filter((r: PortfolioRow) => r.officer_status === 'Approved').length;
  const rejectedCount = portfolioRows.filter((r: PortfolioRow) => r.officer_status === 'Rejected').length;
  const conditionalCount = portfolioRows.filter((r: PortfolioRow) => r.officer_status === 'Conditional').length;

  // --- Filter and Search logic ---
  const filteredData = portfolioRows.filter((app: PortfolioRow) => {
    const matchesSearch = app.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          app.business_id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'All Statuses' || 
                          app.officer_status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="p-6 lg:p-8 w-full max-w-[1440px] mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-text-primary mb-1">Loan Applications</h1>
        <p className="text-sm text-text-secondary">Manage and review all incoming MSME credit requests.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
        <SummaryCard title="Total Applications" value={totalApps} icon={<FileText className="w-5 h-5" />} colorClass="bg-background-muted text-text-secondary" />
        <SummaryCard title="Pending Review" value={pendingCount} icon={<Clock className="w-5 h-5" />} colorClass="bg-warning/10 text-warning" />
        <SummaryCard title="Conditional" value={conditionalCount} icon={<BrainCircuit className="w-5 h-5" />} colorClass="bg-secondary/10 text-secondary" />
        <SummaryCard title="Approved" value={approvedCount} icon={<CheckCircle2 className="w-5 h-5" />} colorClass="bg-success/10 text-success" />
        <SummaryCard title="Rejected" value={rejectedCount} icon={<AlertCircle className="w-5 h-5" />} colorClass="bg-error/10 text-error" />
      </div>

      <div className="bg-white border border-border rounded-card shadow-card overflow-hidden">
        <div className="p-5 border-b border-border flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="relative">
              <Search className="w-4 h-4 text-text-secondary absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="search"
                placeholder="Search business name or ID..."
                aria-label="Search business name or ID"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9 pr-4 py-2 border border-border rounded text-sm focus:outline-none focus:border-primary w-full sm:w-64"
              />
            </div>
            {searchTerm && (
              <button 
                onClick={() => setSearchTerm('')} 
                className="text-xs text-text-secondary hover:text-text-primary"
              >
                Clear
              </button>
            )}
          </div>
          <div className="flex gap-2">
            <select 
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="border border-border rounded px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-primary"
            >
              <option value="All Statuses">All Statuses</option>
              <option value="Pending">Pending</option>
              <option value="Approved">Approved</option>
              <option value="Rejected">Rejected</option>
              <option value="Conditional">Conditional</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-background-muted/30 border-b border-border">
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">App ID</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Business Name</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Industry</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Estimated Loan</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Health Score</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">AI Risk</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Filing Date</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Status</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filteredData.map((app) => (
                <tr key={app.business_id} className="hover:bg-background-muted/30 transition-colors">
                  <td className="px-5 py-4 text-sm font-semibold text-text-primary">{app.business_id}</td>
                  <td className="px-5 py-4 text-sm font-medium text-text-primary">{app.name}</td>
                  <td className="px-5 py-4 text-sm text-text-secondary">{app.industry}</td>
                  <td className="px-5 py-4 text-sm font-semibold text-text-primary tnum">{formatINRCompact(app.avg_monthly_revenue * 3)}</td>
                  <td className="px-5 py-4">
                    <span className={`text-sm font-bold tnum ${app.score >= 75 ? 'text-success' : app.score >= 55 ? 'text-warning' : 'text-error'}`}>
                      {app.score}
                    </span>
                  </td>
                  <td className="px-5 py-4"><RiskBadge risk={app.band} /></td>
                  <td className="px-5 py-4 text-sm text-text-secondary">{app.applied_at}</td>
                  <td className="px-5 py-4"><StatusBadge status={app.officer_status} /></td>
                  <td className="px-5 py-4 text-right">
                    <RouterLink to={`/officer/applications/${app.business_id}`} className="inline-flex items-center gap-1 px-3 py-1.5 bg-primary/10 hover:bg-primary/20 text-primary text-xs font-semibold rounded transition-colors">
                      View Details <ArrowRight className="w-3 h-3" />
                    </RouterLink>
                  </td>
                </tr>
              ))}
              {filteredData.length === 0 && (
                <tr>
                  <td colSpan={9} className="px-5 py-8 text-center text-sm text-text-secondary">
                    No applications match the search query or selected filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        
        <div className="p-4 border-t border-border flex items-center justify-between text-sm text-text-secondary">
          <span>Showing {filteredData.length} of {totalApps} entries</span>
        </div>
      </div>
    </div>
  );
}
