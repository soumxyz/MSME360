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
  const [statusFilter, setStatusFilter] = useState('Pending');

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

  // Filter to show only real-time applications (Pending status)
  const realtimeApps = portfolioRows.filter((r: PortfolioRow) => r.officer_status === 'Pending');

  // --- Dynamic Stats Computations ---
  const totalApps = realtimeApps.length;
  const pendingCount = realtimeApps.filter((r: PortfolioRow) => r.officer_status === 'Pending').length;
  const approvedCount = portfolioRows.filter((r: PortfolioRow) => r.officer_status === 'Approved').length;
  const rejectedCount = portfolioRows.filter((r: PortfolioRow) => r.officer_status === 'Rejected').length;
  const conditionalCount = portfolioRows.filter((r: PortfolioRow) => r.officer_status === 'Conditional').length;

  // --- Filter and Search logic ---
  const filteredData = realtimeApps.filter((app: PortfolioRow) => {
    const matchesSearch = app.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          app.business_id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'All Statuses' || 
                          app.officer_status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="p-6 lg:p-8 w-full max-w-[1440px] mx-auto">
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-semibold text-text-primary mb-1">Real-Time Loan Applications</h1>
            <p className="text-sm text-text-secondary">Review and process incoming MSME credit applications awaiting decision.</p>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-success/10 border border-success/20 rounded">
            <div className="w-2 h-2 bg-success rounded-full animate-pulse" />
            <span className="text-sm font-medium text-success">Live Queue</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
        <SummaryCard title="Awaiting Review" value={totalApps} icon={<FileText className="w-5 h-5" />} colorClass="bg-warning/10 text-warning" />
        <SummaryCard title="Pending Review" value={pendingCount} icon={<Clock className="w-5 h-5" />} colorClass="bg-warning/10 text-warning" />
        <SummaryCard title="Conditional" value={conditionalCount} icon={<BrainCircuit className="w-5 h-5" />} colorClass="bg-secondary/10 text-secondary" />
        <SummaryCard title="Approved" value={approvedCount} icon={<CheckCircle2 className="w-5 h-5" />} colorClass="bg-success/10 text-success" />
        <SummaryCard title="Rejected" value={rejectedCount} icon={<AlertCircle className="w-5 h-5" />} colorClass="bg-error/10 text-error" />
      </div>

      <div className="bg-white border border-border rounded-card shadow-card overflow-hidden">
        <div className="p-5 bg-gradient-to-r from-primary/5 to-transparent border-b border-border">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-lg font-semibold text-text-primary mb-1">Application Queue</h2>
              <p className="text-xs text-text-secondary">Real-time pending applications requiring review</p>
            </div>
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="w-4 h-4 text-text-secondary absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="search"
                  placeholder="Search business name or ID..."
                  aria-label="Search business name or ID"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-9 pr-4 py-2 border border-border rounded text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary w-full sm:w-64"
                />
              </div>
              {searchTerm && (
                <button 
                  onClick={() => setSearchTerm('')} 
                  className="text-xs text-primary hover:text-primary-hover font-medium"
                >
                  Clear
                </button>
              )}
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gradient-to-r from-primary to-primary-hover text-white">
                <th className="px-5 py-3.5 text-xs font-semibold uppercase tracking-wider">App ID</th>
                <th className="px-5 py-3.5 text-xs font-semibold uppercase tracking-wider">Business Name</th>
                <th className="px-5 py-3.5 text-xs font-semibold uppercase tracking-wider">Industry</th>
                <th className="px-5 py-3.5 text-xs font-semibold uppercase tracking-wider">Estimated Loan</th>
                <th className="px-5 py-3.5 text-xs font-semibold uppercase tracking-wider">Health Score</th>
                <th className="px-5 py-3.5 text-xs font-semibold uppercase tracking-wider">AI Risk</th>
                <th className="px-5 py-3.5 text-xs font-semibold uppercase tracking-wider">Filing Date</th>
                <th className="px-5 py-3.5 text-xs font-semibold uppercase tracking-wider">Status</th>
                <th className="px-5 py-3.5 text-xs font-semibold uppercase tracking-wider text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filteredData.map((app, idx) => (
                <tr key={app.business_id} className={`hover:bg-primary/5 transition-colors ${idx % 2 === 0 ? 'bg-white' : 'bg-background-muted/20'}`}>
                  <td className="px-5 py-4 text-sm font-semibold text-primary">{app.business_id}</td>
                  <td className="px-5 py-4 text-sm font-medium text-text-primary">{app.name}</td>
                  <td className="px-5 py-4 text-sm text-text-secondary">{app.industry}</td>
                  <td className="px-5 py-4 text-sm font-semibold text-text-primary tnum">{formatINRCompact(app.avg_monthly_revenue * 3)}</td>
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-2">
                      <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-sm ${
                        app.score >= 75 ? 'bg-success/10 text-success border-2 border-success' : 
                        app.score >= 55 ? 'bg-warning/10 text-warning border-2 border-warning' : 
                        'bg-error/10 text-error border-2 border-error'
                      }`}>
                        {app.score}
                      </div>
                    </div>
                  </td>
                  <td className="px-5 py-4"><RiskBadge risk={app.band} /></td>
                  <td className="px-5 py-4 text-sm text-text-secondary">{app.applied_at}</td>
                  <td className="px-5 py-4"><StatusBadge status={app.officer_status} /></td>
                  <td className="px-5 py-4 text-right">
                    <RouterLink to={`/officer/applications/${app.business_id}`} className="inline-flex items-center gap-1 px-4 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-semibold rounded shadow-sm transition-all hover:shadow-md">
                      Review <ArrowRight className="w-3 h-3" />
                    </RouterLink>
                  </td>
                </tr>
              ))}
              {filteredData.length === 0 && (
                <tr>
                  <td colSpan={9} className="px-5 py-12 text-center">
                    <div className="flex flex-col items-center gap-2">
                      <FileText className="w-12 h-12 text-text-secondary opacity-30" />
                      <p className="text-sm font-medium text-text-secondary">No pending applications found</p>
                      <p className="text-xs text-text-secondary">All applications have been processed or no matches for your search</p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        
        <div className="p-4 bg-background-muted/30 border-t border-border flex items-center justify-between text-sm text-text-secondary">
          <span>Showing <strong className="text-text-primary">{filteredData.length}</strong> of <strong className="text-text-primary">{totalApps}</strong> pending applications</span>
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4" />
            <span className="text-xs">Last updated: Just now</span>
          </div>
        </div>
      </div>
    </div>
  );
}
