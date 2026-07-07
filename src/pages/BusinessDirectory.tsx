import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Search, 
  Filter, 
  Building2,
  ExternalLink
} from 'lucide-react';

const directoryData = [
  {
    id: 'B-1001',
    business: 'Acme Industries Pvt Ltd',
    industry: 'Manufacturing',
    gstin: '22AAAAA0000A1Z5',
    healthScore: 82,
    risk: 'Low',
    exposure: '₹2.5 Cr',
    lastReview: '05 Jul 2026'
  },
  {
    id: 'B-1002',
    business: 'Global Tech Solutions',
    industry: 'IT Services',
    gstin: '27AABCB1234K1Z0',
    healthScore: 68,
    risk: 'Medium',
    exposure: '₹50 L',
    lastReview: '01 Jun 2026'
  },
  {
    id: 'B-1003',
    business: 'Apex Logistics Co.',
    industry: 'Transportation',
    gstin: '09AAACA8888H1Z8',
    healthScore: 45,
    risk: 'High',
    exposure: '₹4.2 Cr',
    lastReview: '15 May 2026'
  },
  {
    id: 'B-1004',
    business: 'Modern Retailers',
    industry: 'Retail',
    gstin: '07BBDCB9999M1Z9',
    healthScore: 91,
    risk: 'Low',
    exposure: '₹0',
    lastReview: '10 Apr 2026'
  }
];

const RiskBadge = ({ risk }: { risk: string }) => {
  if (risk === 'Low') return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-success/10 text-success border border-success/20">Low Risk</span>;
  if (risk === 'Medium') return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-warning/10 text-warning border border-warning/20">Med Risk</span>;
  return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-error/10 text-error border border-error/20">High Risk</span>;
};

export default function BusinessDirectory() {
  return (
    <div className="p-6 lg:p-8 w-full max-w-[1440px] mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-text-primary mb-1">Business Directory</h1>
        <p className="text-sm text-text-secondary">Comprehensive CRM of all connected MSME clients.</p>
      </div>

      <div className="bg-white border border-border rounded-card shadow-card overflow-hidden">
        <div className="p-5 border-b border-border flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex flex-1 items-center gap-2">
            <div className="relative flex-1 max-w-md">
              <Search className="w-4 h-4 text-text-secondary absolute left-3 top-1/2 -translate-y-1/2" />
              <input 
                type="text" 
                placeholder="Search business name, GSTIN..." 
                className="pl-9 pr-4 py-2 border border-border rounded text-sm focus:outline-none focus:border-primary w-full"
              />
            </div>
            <button className="flex items-center gap-2 px-4 py-2 border border-border bg-white hover:bg-background-muted rounded text-sm font-medium text-text-primary transition-colors">
              <Filter className="w-4 h-4" /> Filters
            </button>
          </div>
          <div className="flex gap-2">
            <select className="border border-border rounded px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-primary">
              <option>All Industries</option>
              <option>Manufacturing</option>
              <option>IT Services</option>
              <option>Transportation</option>
              <option>Retail</option>
            </select>
            <select className="border border-border rounded px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-primary">
              <option>All Risks</option>
              <option>Low Risk</option>
              <option>Medium Risk</option>
              <option>High Risk</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-background-muted/30 border-b border-border">
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Business</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Industry</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">GSTIN</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Health Score</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Risk</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Loan Exposure</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Last Review</th>
                <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {directoryData.map((biz) => (
                <tr key={biz.id} className="hover:bg-background-muted/30 transition-colors">
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded bg-background-muted border border-border flex items-center justify-center flex-shrink-0">
                        <Building2 className="w-4 h-4 text-text-secondary" />
                      </div>
                      <span className="text-sm font-semibold text-text-primary">{biz.business}</span>
                    </div>
                  </td>
                  <td className="px-5 py-4 text-sm text-text-secondary">{biz.industry}</td>
                  <td className="px-5 py-4 text-sm font-medium text-text-primary">{biz.gstin}</td>
                  <td className="px-5 py-4">
                    <span className={`text-sm font-bold ${biz.healthScore >= 80 ? 'text-success' : biz.healthScore >= 60 ? 'text-warning' : 'text-error'}`}>
                      {biz.healthScore}
                    </span>
                  </td>
                  <td className="px-5 py-4"><RiskBadge risk={biz.risk} /></td>
                  <td className="px-5 py-4 text-sm font-semibold text-text-primary">{biz.exposure}</td>
                  <td className="px-5 py-4 text-sm text-text-secondary">{biz.lastReview}</td>
                  <td className="px-5 py-4 text-right">
                    <Link to={`/officer/health-cards`} className="inline-flex items-center gap-1 px-3 py-1.5 bg-white border border-border hover:bg-background-muted text-text-secondary text-xs font-medium rounded transition-colors">
                      Open Card <ExternalLink className="w-3 h-3" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        <div className="p-4 border-t border-border flex items-center justify-between text-sm text-text-secondary">
          <span>Showing 1 to 4 of 3,429 entries</span>
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
