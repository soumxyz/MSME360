import React from 'react';
import { Link } from 'react-router-dom';
import { 
  FileText, 
  CheckCircle2, 
  Clock, 
  AlertCircle, 
  Search,
  Eye
} from 'lucide-react';

const applications = [
  {
    id: 'APP-10294',
    type: 'Working Capital Loan',
    amount: '₹2.5 Cr',
    date: '05 Jul 2026',
    status: 'Under Review',
    decision: 'Expected by 08 Jul'
  },
  {
    id: 'APP-09832',
    type: 'Machinery Term Loan',
    amount: '₹1.2 Cr',
    date: '12 Mar 2026',
    status: 'Approved',
    decision: 'Disbursed'
  },
  {
    id: 'APP-08421',
    type: 'Business Expansion',
    amount: '₹5.0 Cr',
    date: '10 Jan 2026',
    status: 'Rejected',
    decision: 'Closed'
  }
];

const SummaryCard = ({ title, value, icon, colorClass }: any) => (
  <div className="bg-white border border-border rounded-card p-5 shadow-card flex items-center justify-between">
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
  if (status === 'Approved') return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-success/10 text-success border border-success/20">Approved</span>;
  if (status === 'Rejected') return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-error/10 text-error border border-error/20">Rejected</span>;
  if (status === 'Under Review') return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-primary/10 text-primary border border-primary/20">Under Review</span>;
  return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-warning/10 text-warning border border-warning/20">{status}</span>;
};

export default function Applications() {
  return (
    <div className="p-6 lg:p-8 w-full max-w-[1440px] mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-text-primary mb-1">My Applications</h1>
        <p className="text-sm text-text-secondary">Track and manage your loan requests.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <SummaryCard 
          title="Total Applications" 
          value="3" 
          icon={<FileText className="w-5 h-5" />} 
          colorClass="bg-background-muted text-text-secondary"
        />
        <SummaryCard 
          title="Approved" 
          value="1" 
          icon={<CheckCircle2 className="w-5 h-5" />} 
          colorClass="bg-success/10 text-success"
        />
        <SummaryCard 
          title="Under Review" 
          value="1" 
          icon={<Clock className="w-5 h-5" />} 
          colorClass="bg-primary/10 text-primary"
        />
        <SummaryCard 
          title="Rejected" 
          value="1" 
          icon={<AlertCircle className="w-5 h-5" />} 
          colorClass="bg-error/10 text-error"
        />
      </div>

      <div className="bg-white border border-border rounded-card shadow-card overflow-hidden">
        <div className="px-5 py-4 border-b border-border flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white">
          <h3 className="text-base font-semibold text-text-primary">Application History</h3>
          <div className="relative">
            <Search className="w-4 h-4 text-text-secondary absolute left-3 top-1/2 -translate-y-1/2" />
            <input 
              type="text" 
              placeholder="Search applications..." 
              className="pl-9 pr-4 py-1.5 border border-border rounded text-sm focus:outline-none focus:border-primary w-full sm:w-64"
            />
          </div>
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
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Expected Decision</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {applications.map((app) => (
                <tr key={app.id} className="hover:bg-background-muted/30 transition-colors">
                  <td className="px-5 py-4">
                    <span className="text-sm font-semibold text-text-primary">{app.id}</span>
                  </td>
                  <td className="px-5 py-4 text-sm text-text-secondary">{app.type}</td>
                  <td className="px-5 py-4 text-sm font-medium text-text-primary">{app.amount}</td>
                  <td className="px-5 py-4 text-sm text-text-secondary">{app.date}</td>
                  <td className="px-5 py-4">
                    <StatusBadge status={app.status} />
                  </td>
                  <td className="px-5 py-4 text-sm text-text-secondary">{app.decision}</td>
                  <td className="px-5 py-4 text-right">
                    <Link to={`/customer/applications/${app.id}`} className="inline-flex items-center justify-center w-8 h-8 rounded border border-border hover:bg-background-muted text-text-secondary transition-colors">
                      <Eye className="w-4 h-4" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
