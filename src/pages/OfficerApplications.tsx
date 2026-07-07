import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Search, 
  Filter, 
  FileText, 
  Clock, 
  BrainCircuit, 
  CheckCircle2, 
  AlertCircle,
  ArrowRight
} from 'lucide-react';

const applicationsData = [
  {
    id: 'APP-10294',
    business: 'Acme Industries Pvt Ltd',
    industry: 'Manufacturing',
    loan: '₹2.5 Cr',
    healthScore: 82,
    aiRisk: 'Low',
    officer: 'Rajesh Kumar',
    date: '05 Jul 2026',
    status: 'Pending'
  },
  {
    id: 'APP-10295',
    business: 'Global Tech Solutions',
    industry: 'IT Services',
    loan: '₹50 Lakhs',
    healthScore: 68,
    aiRisk: 'Medium',
    officer: 'Unassigned',
    date: '06 Jul 2026',
    status: 'AI Recommended'
  },
  {
    id: 'APP-10296',
    business: 'Apex Logistics Co.',
    industry: 'Transportation',
    loan: '₹1.2 Cr',
    healthScore: 45,
    aiRisk: 'High',
    officer: 'Priya Sharma',
    date: '06 Jul 2026',
    status: 'Rejected'
  },
  {
    id: 'APP-10297',
    business: 'Modern Retailers',
    industry: 'Retail',
    loan: '₹75 Lakhs',
    healthScore: 91,
    aiRisk: 'Low',
    officer: 'Amit Patel',
    date: '07 Jul 2026',
    status: 'Approved'
  }
];

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
    case 'AI Recommended':
      return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-primary/10 text-primary border border-primary/20">AI Recommended</span>;
    case 'Pending':
      return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-warning/10 text-warning border border-warning/20">Pending</span>;
    default:
      return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-background-muted text-text-secondary border border-border">{status}</span>;
  }
};

const RiskBadge = ({ risk }: { risk: string }) => {
  if (risk === 'Low') return <span className="text-success font-medium text-sm">Low</span>;
  if (risk === 'Medium') return <span className="text-warning font-medium text-sm">Medium</span>;
  return <span className="text-error font-medium text-sm">High</span>;
};

export default function OfficerApplications() {
  return (
    <div className="p-6 lg:p-8 w-full max-w-[1440px] mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-text-primary mb-1">Loan Applications</h1>
        <p className="text-sm text-text-secondary">Manage and review all incoming MSME credit requests.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
        <SummaryCard title="Total Applications" value="124" icon={<FileText className="w-5 h-5" />} colorClass="bg-background-muted text-text-secondary" />
        <SummaryCard title="Pending" value="45" icon={<Clock className="w-5 h-5" />} colorClass="bg-warning/10 text-warning" />
        <SummaryCard title="AI Recommended" value="38" icon={<BrainCircuit className="w-5 h-5" />} colorClass="bg-primary/10 text-primary" />
        <SummaryCard title="Approved" value="29" icon={<CheckCircle2 className="w-5 h-5" />} colorClass="bg-success/10 text-success" />
        <SummaryCard title="Rejected" value="12" icon={<AlertCircle className="w-5 h-5" />} colorClass="bg-error/10 text-error" />
      </div>

      <div className="bg-white border border-border rounded-card shadow-card overflow-hidden">
        <div className="p-5 border-b border-border flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="relative">
              <Search className="w-4 h-4 text-text-secondary absolute left-3 top-1/2 -translate-y-1/2" />
              <input 
                type="text" 
                placeholder="Search business or ID..." 
                className="pl-9 pr-4 py-2 border border-border rounded text-sm focus:outline-none focus:border-primary w-full sm:w-64"
              />
            </div>
            <button className="flex items-center gap-2 px-4 py-2 border border-border bg-white hover:bg-background-muted rounded text-sm font-medium text-text-primary transition-colors">
              <Filter className="w-4 h-4" /> Filters
            </button>
          </div>
          <div className="flex gap-2">
            <select className="border border-border rounded px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-primary">
              <option>All Statuses</option>
              <option>Pending</option>
              <option>Approved</option>
              <option>Rejected</option>
              <option>AI Recommended</option>
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
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Loan</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Health Score</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">AI Risk</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Officer</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Date</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Status</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {applicationsData.map((app) => (
                <tr key={app.id} className="hover:bg-background-muted/30 transition-colors">
                  <td className="px-5 py-4 text-sm font-semibold text-text-primary">{app.id}</td>
                  <td className="px-5 py-4 text-sm font-medium text-text-primary">{app.business}</td>
                  <td className="px-5 py-4 text-sm text-text-secondary">{app.industry}</td>
                  <td className="px-5 py-4 text-sm font-semibold text-text-primary">{app.loan}</td>
                  <td className="px-5 py-4">
                    <span className={`text-sm font-bold ${app.healthScore >= 80 ? 'text-success' : app.healthScore >= 60 ? 'text-warning' : 'text-error'}`}>
                      {app.healthScore}
                    </span>
                  </td>
                  <td className="px-5 py-4"><RiskBadge risk={app.aiRisk} /></td>
                  <td className="px-5 py-4 text-sm text-text-secondary">{app.officer}</td>
                  <td className="px-5 py-4 text-sm text-text-secondary">{app.date}</td>
                  <td className="px-5 py-4"><StatusBadge status={app.status} /></td>
                  <td className="px-5 py-4 text-right">
                    <Link to={`/officer/applications/${app.id}`} className="inline-flex items-center gap-1 px-3 py-1.5 bg-primary/10 hover:bg-primary/20 text-primary text-xs font-semibold rounded transition-colors">
                      View Details <ArrowRight className="w-3 h-3" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        <div className="p-4 border-t border-border flex items-center justify-between text-sm text-text-secondary">
          <span>Showing 1 to 4 of 124 entries</span>
          <div className="flex gap-1">
            <button className="px-3 py-1 border border-border rounded hover:bg-background-muted">Prev</button>
            <button className="px-3 py-1 border border-border rounded bg-primary text-white">1</button>
            <button className="px-3 py-1 border border-border rounded hover:bg-background-muted">2</button>
            <button className="px-3 py-1 border border-border rounded hover:bg-background-muted">3</button>
            <button className="px-3 py-1 border border-border rounded hover:bg-background-muted">Next</button>
          </div>
        </div>
      </div>
    </div>
  );
}
