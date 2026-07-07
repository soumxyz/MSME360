import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ShieldAlert, 
  AlertTriangle, 
  Search, 
  Filter,
  ArrowRight,
  ShieldCheck
} from 'lucide-react';

const riskData = [
  {
    id: 'RQ-001',
    business: 'Apex Logistics Co.',
    riskLevel: 'Critical',
    confidence: '98%',
    reason: 'Severe GST mismatch & Cashflow anomaly',
    officer: 'Unassigned',
    status: 'Action Required',
    appId: 'APP-10296'
  },
  {
    id: 'RQ-002',
    business: 'Sunrise Exporters',
    riskLevel: 'High',
    confidence: '92%',
    reason: 'Revenue decline & High customer churn',
    officer: 'Rajesh Kumar',
    status: 'In Review',
    appId: null
  },
  {
    id: 'RQ-003',
    business: 'Global Tech Solutions',
    riskLevel: 'Medium',
    confidence: '85%',
    reason: 'Customer concentration risk',
    officer: 'Priya Sharma',
    status: 'Action Required',
    appId: 'APP-10295'
  },
  {
    id: 'RQ-004',
    business: 'Acme Industries Pvt Ltd',
    riskLevel: 'Low',
    confidence: '95%',
    reason: 'Routine periodic review',
    officer: 'Unassigned',
    status: 'Monitoring',
    appId: 'APP-10294'
  }
];

const SummaryCard = ({ title, value, colorClass }: any) => (
  <div className="bg-white border border-border rounded-card p-5 shadow-sm flex items-center justify-between">
    <div>
      <p className="text-xs font-medium text-text-secondary mb-1">{title}</p>
      <h3 className="text-2xl font-bold text-text-primary">{value}</h3>
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

export default function RiskQueue() {
  return (
    <div className="p-6 lg:p-8 w-full max-w-[1440px] mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-text-primary mb-1">Risk Queue</h1>
        <p className="text-sm text-text-secondary">Businesses requiring officer attention prioritized by AI risk severity.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <SummaryCard title="Critical Alerts" value="12" colorClass="bg-error" />
        <SummaryCard title="High Risk" value="45" colorClass="bg-error/60" />
        <SummaryCard title="Medium Risk" value="128" colorClass="bg-warning" />
        <SummaryCard title="Low / Routine" value="892" colorClass="bg-success" />
      </div>

      <div className="bg-white border border-border rounded-card shadow-card overflow-hidden">
        <div className="p-5 border-b border-border flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="relative">
              <Search className="w-4 h-4 text-text-secondary absolute left-3 top-1/2 -translate-y-1/2" />
              <input 
                type="text" 
                placeholder="Search queue..." 
                className="pl-9 pr-4 py-2 border border-border rounded text-sm focus:outline-none focus:border-primary w-full sm:w-64"
              />
            </div>
            <button className="flex items-center gap-2 px-4 py-2 border border-border bg-white hover:bg-background-muted rounded text-sm font-medium text-text-primary transition-colors">
              <Filter className="w-4 h-4" /> Filters
            </button>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm text-text-secondary flex items-center gap-1"><ShieldCheck className="w-4 h-4 text-success" /> Auto-sorted by severity</span>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-background-muted/30 border-b border-border">
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Business</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Risk Level</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">AI Confidence</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Reason</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Officer</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Status</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {riskData.map((item) => (
                <tr key={item.id} className="hover:bg-background-muted/30 transition-colors">
                  <td className="px-5 py-4 text-sm font-semibold text-text-primary">{item.business}</td>
                  <td className="px-5 py-4"><RiskBadge risk={item.riskLevel} /></td>
                  <td className="px-5 py-4 text-sm font-medium text-text-primary">{item.confidence}</td>
                  <td className="px-5 py-4 text-sm text-text-secondary max-w-xs truncate">{item.reason}</td>
                  <td className="px-5 py-4 text-sm text-text-secondary">{item.officer}</td>
                  <td className="px-5 py-4">
                    <span className={`text-xs font-medium ${item.status === 'Action Required' ? 'text-error' : 'text-text-secondary'}`}>
                      {item.status}
                    </span>
                  </td>
                  <td className="px-5 py-4 text-right">
                    {item.appId ? (
                      <Link to={`/officer/applications/${item.appId}`} className="inline-flex items-center gap-1 px-3 py-1.5 bg-primary/10 hover:bg-primary/20 text-primary text-xs font-semibold rounded transition-colors">
                        Investigate <ArrowRight className="w-3 h-3" />
                      </Link>
                    ) : (
                      <button className="inline-flex items-center gap-1 px-3 py-1.5 bg-white border border-border hover:bg-background-muted text-text-secondary text-xs font-medium rounded transition-colors">
                        View Profile
                      </button>
                    )}
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
