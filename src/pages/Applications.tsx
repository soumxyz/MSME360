import React from 'react';
import { Link } from 'react-router-dom';
import {
  FileText,
  CheckCircle2,
  Clock,
  AlertCircle,
  Eye
} from 'lucide-react';
import { useBusinessDetail } from '../lib/api/hooks';
import { DEMO_BUSINESS_ID } from '../lib/customer';
import { formatINRCompact, formatDate } from '../lib/format';
import { PageSkeleton } from '../components/Skeleton';

const SummaryCard = ({ title, value, icon, colorClass }: any) => (
  <div className="bg-white border border-border rounded-card p-5 shadow-card flex items-center justify-between">
    <div>
      <p className="text-xs font-medium text-text-secondary mb-1">{title}</p>
      <h3 className="text-2xl font-bold text-text-primary tnum">{value}</h3>
    </div>
    <div className={`p-3 rounded ${colorClass}`}>
      {icon}
    </div>
  </div>
);

const StatusBadge = ({ status }: { status: string }) => {
  if (status === 'Approved') return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-success/10 text-success border border-success/20">Approved</span>;
  if (status === 'Rejected') return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-error/10 text-error border border-error/20">Rejected</span>;
  if (status === 'Pending') return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-primary/10 text-primary border border-primary/20">Under Review</span>;
  return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-warning/10 text-warning border border-warning/20">{status}</span>;
};

export default function Applications() {
  const { data, isLoading, error } = useBusinessDetail(DEMO_BUSINESS_ID);

  if (isLoading) return <PageSkeleton label="Loading your applications" />;
  if (error || !data) {
    return (
      <div className="p-6 text-center text-error">
        <p className="font-semibold">Error loading applications</p>
        <p className="text-xs mt-1">Make sure the FastAPI server is running on port 8000.</p>
      </div>
    );
  }

  const status = data.officer_status;
  const isDecided = status !== 'Pending';

  return (
    <div className="p-6 lg:p-8 w-full max-w-[1440px] mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-text-primary mb-1">My Applications</h1>
        <p className="text-sm text-text-secondary">Track and manage the loan requests of {data.profile.name}.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <SummaryCard
          title="Active Applications"
          value={1}
          icon={<FileText className="w-5 h-5" />}
          colorClass="bg-background-muted text-text-secondary"
        />
        <SummaryCard
          title="Approved"
          value={status === 'Approved' || status === 'Conditional' ? 1 : 0}
          icon={<CheckCircle2 className="w-5 h-5" />}
          colorClass="bg-success/10 text-success"
        />
        <SummaryCard
          title="Under Review"
          value={status === 'Pending' || status === 'Info Requested' ? 1 : 0}
          icon={<Clock className="w-5 h-5" />}
          colorClass="bg-primary/10 text-primary"
        />
        <SummaryCard
          title="Rejected"
          value={status === 'Rejected' ? 1 : 0}
          icon={<AlertCircle className="w-5 h-5" />}
          colorClass="bg-error/10 text-error"
        />
      </div>

      <div className="bg-white border border-border rounded-card shadow-card overflow-hidden">
        <div className="px-5 py-4 border-b border-border bg-white">
          <h3 className="text-base font-semibold text-text-primary">Application History</h3>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-background-muted/50 border-b border-border">
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">App Number</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Loan Type</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Amount</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Date</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Status</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Stage</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              <tr className="hover:bg-background-muted/30 transition-colors">
                <td className="px-5 py-4">
                  <span className="text-sm font-semibold text-text-primary">{data.business_id}</span>
                </td>
                <td className="px-5 py-4 text-sm text-text-secondary">Working Capital Loan</td>
                <td className="px-5 py-4 text-sm font-medium text-text-primary tnum">{formatINRCompact(data.recommendation.loan_amount)}</td>
                <td className="px-5 py-4 text-sm text-text-secondary">{formatDate(data.applied_at)}</td>
                <td className="px-5 py-4"><StatusBadge status={status} /></td>
                <td className="px-5 py-4 text-sm text-text-secondary">
                  {isDecided ? 'Officer decision recorded' : 'With credit officer'}
                </td>
                <td className="px-5 py-4 text-right">
                  <Link
                    to={`/customer/applications/${data.business_id}`}
                    aria-label="View application details"
                    className="inline-flex items-center justify-center w-8 h-8 rounded border border-border hover:bg-background-muted text-text-secondary transition-colors"
                  >
                    <Eye className="w-4 h-4" aria-hidden="true" />
                  </Link>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
