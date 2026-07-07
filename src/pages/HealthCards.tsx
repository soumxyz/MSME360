import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Search, 
  Filter, 
  Download, 
  Eye, 
  History, 
  GitCompare,
  Activity
} from 'lucide-react';

const healthCardData = [
  {
    id: 'HC-001',
    business: 'Acme Industries Pvt Ltd',
    healthScore: 82,
    grade: 'A-',
    risk: 'Low',
    generatedDate: '07 Jul 2026',
  },
  {
    id: 'HC-002',
    business: 'Global Tech Solutions',
    healthScore: 68,
    grade: 'B+',
    risk: 'Medium',
    generatedDate: '01 Jun 2026',
  },
  {
    id: 'HC-003',
    business: 'Apex Logistics Co.',
    healthScore: 45,
    grade: 'C-',
    risk: 'High',
    generatedDate: '15 May 2026',
  },
  {
    id: 'HC-004',
    business: 'Modern Retailers',
    healthScore: 91,
    grade: 'A+',
    risk: 'Low',
    generatedDate: '10 Apr 2026',
  }
];

const RiskBadge = ({ risk }: { risk: string }) => {
  if (risk === 'Low') return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-success/10 text-success border border-success/20">Low Risk</span>;
  if (risk === 'Medium') return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-warning/10 text-warning border border-warning/20">Med Risk</span>;
  return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-error/10 text-error border border-error/20">High Risk</span>;
};

export default function HealthCards() {
  return (
    <div className="p-6 lg:p-8 w-full max-w-[1440px] mx-auto">
      <div className="mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary mb-1">Financial Health Cards</h1>
          <p className="text-sm text-text-secondary">Repository of all AI-generated financial health assessments.</p>
        </div>
        <button className="bg-primary hover:bg-primary-hover text-white px-4 py-2 rounded text-sm font-medium transition-colors flex items-center gap-2">
          <Activity className="w-4 h-4" /> Generate New Card
        </button>
      </div>

      <div className="bg-white border border-border rounded-card shadow-card overflow-hidden">
        <div className="p-5 border-b border-border flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="relative">
              <Search className="w-4 h-4 text-text-secondary absolute left-3 top-1/2 -translate-y-1/2" />
              <input 
                type="text" 
                placeholder="Search business..." 
                className="pl-9 pr-4 py-2 border border-border rounded text-sm focus:outline-none focus:border-primary w-full sm:w-64"
              />
            </div>
            <button className="flex items-center gap-2 px-4 py-2 border border-border bg-white hover:bg-background-muted rounded text-sm font-medium text-text-primary transition-colors">
              <Filter className="w-4 h-4" /> Filters
            </button>
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
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Generated Date</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {healthCardData.map((card) => (
                <tr key={card.id} className="hover:bg-background-muted/30 transition-colors">
                  <td className="px-5 py-4 text-sm font-semibold text-text-primary">{card.business}</td>
                  <td className="px-5 py-4">
                    <span className={`text-sm font-bold ${card.healthScore >= 80 ? 'text-success' : card.healthScore >= 60 ? 'text-warning' : 'text-error'}`}>
                      {card.healthScore}
                    </span>
                  </td>
                  <td className="px-5 py-4 text-sm font-bold text-text-primary">{card.grade}</td>
                  <td className="px-5 py-4"><RiskBadge risk={card.risk} /></td>
                  <td className="px-5 py-4 text-sm text-text-secondary">{card.generatedDate}</td>
                  <td className="px-5 py-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Link to="/customer/reports" className="inline-flex items-center justify-center w-8 h-8 rounded bg-primary/10 hover:bg-primary/20 text-primary transition-colors tooltip-trigger" title="Open Card">
                        <Eye className="w-4 h-4" />
                      </Link>
                      <button className="inline-flex items-center justify-center w-8 h-8 rounded border border-border hover:bg-background-muted text-text-secondary transition-colors" title="Download PDF">
                        <Download className="w-4 h-4" />
                      </button>
                      <button className="inline-flex items-center justify-center w-8 h-8 rounded border border-border hover:bg-background-muted text-text-secondary transition-colors" title="Compare">
                        <GitCompare className="w-4 h-4" />
                      </button>
                      <button className="inline-flex items-center justify-center w-8 h-8 rounded border border-border hover:bg-background-muted text-text-secondary transition-colors" title="History">
                        <History className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        <div className="p-4 border-t border-border flex items-center justify-between text-sm text-text-secondary">
          <span>Showing 1 to 4 of 1,205 entries</span>
          <div className="flex gap-1">
            <button className="px-3 py-1 border border-border rounded hover:bg-background-muted">Prev</button>
            <button className="px-3 py-1 border border-border rounded bg-primary text-white">1</button>
            <button className="px-3 py-1 border border-border rounded hover:bg-background-muted">Next</button>
          </div>
        </div>
      </div>
    </div>
  );
}
