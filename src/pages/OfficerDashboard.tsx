import React from 'react';
import { 
  Activity, 
  FileCheck, 
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock,
  Eye,
  AlertOctagon,
  SearchCode,
  FileWarning,
  BrainCircuit
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  ResponsiveContainer,
  PieChart as RechartsPie,
  Pie,
  Cell,
  Tooltip,
  Legend
} from 'recharts';

// --- Mock Data ---
const tableData = [
  { id: 'APP-8921', business: 'Acme Industries Pvt Ltd', score: 82, risk: 'Low', loan: '₹2.5 Cr (WC)', officer: 'Rajesh K.', status: 'Pending Review' },
  { id: 'APP-8922', business: 'TechFlow Solutions', score: 94, risk: 'Low', loan: '₹50 L (Expansion)', officer: 'Meera S.', status: 'Approved' },
  { id: 'APP-8923', business: 'Global Logistics', score: 45, risk: 'High', loan: '₹1.2 Cr (Vehicle)', officer: 'Amit V.', status: 'Rejected' },
  { id: 'APP-8924', business: 'Sunrise Retail', score: 68, risk: 'Medium', loan: '₹75 L (WC)', officer: 'Rajesh K.', status: 'AI Recommended' },
  { id: 'APP-8925', business: 'Prime Manufacturing', score: 71, risk: 'Medium', loan: '₹3.0 Cr (Machinery)', officer: 'Neha P.', status: 'Pending Review' },
];

const portfolioData = [
  { name: 'Working Capital', value: 45 },
  { name: 'Term Loans', value: 30 },
  { name: 'Machinery', value: 15 },
  { name: 'Vehicle', value: 10 },
];

const industryData = [
  { name: 'Mfg', value: 35 },
  { name: 'Retail', value: 25 },
  { name: 'IT/Tech', value: 20 },
  { name: 'Logistics', value: 15 },
  { name: 'Other', value: 5 },
];

const riskDistData = [
  { name: 'Low Risk', value: 65 },
  { name: 'Medium Risk', value: 25 },
  { name: 'High Risk', value: 10 },
];

const COLORS = ['#0F4C81', '#2563EB', '#60A5FA', '#93C5FD', '#BFDBFE'];
const RISK_COLORS = ['#16A34A', '#D97706', '#DC2626'];

const SummaryCard = ({ title, value, icon, highlightColor = 'text-primary', bgColor = 'bg-primary/10' }: any) => (
  <div className="bg-white border border-border rounded-card p-5 shadow-card flex items-center justify-between">
    <div>
      <p className="text-xs font-medium text-text-secondary mb-1">{title}</p>
      <h3 className={`text-2xl font-bold text-text-primary`}>{value}</h3>
    </div>
    <div className={`p-3 rounded ${bgColor} ${highlightColor}`}>
      {icon}
    </div>
  </div>
);

const ChartCard = ({ title, children }: { title: string, children: React.ReactNode }) => (
  <div className="bg-white border border-border rounded-card p-5 shadow-card flex flex-col h-full">
    <h3 className="text-sm font-semibold text-text-primary mb-4">{title}</h3>
    <div className="flex-grow w-full h-[200px]">
      {children}
    </div>
  </div>
);

const StatusBadge = ({ status }: { status: string }) => {
  if (status === 'Approved') return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-success/10 text-success border border-success/20">Approved</span>;
  if (status === 'Rejected') return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-error/10 text-error border border-error/20">Rejected</span>;
  if (status === 'AI Recommended') return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-primary/10 text-primary border border-primary/20">AI Recommended</span>;
  return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-warning/10 text-warning border border-warning/20">Pending</span>;
};

const RiskBadge = ({ risk }: { risk: string }) => {
  if (risk === 'High') return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-error/10 text-error">High</span>;
  if (risk === 'Medium') return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-warning/10 text-warning">Medium</span>;
  return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-success/10 text-success">Low</span>;
};

export default function OfficerDashboard() {
  return (
    <div className="p-6 lg:p-8 w-full mx-auto">
      
      {/* Summary Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4 mb-6">
        <SummaryCard 
          title="Today's Apps" 
          value="42" 
          icon={<FileCheck className="w-5 h-5" />} 
        />
        <SummaryCard 
          title="Avg Health Score" 
          value="76" 
          icon={<Activity className="w-5 h-5" />} 
          highlightColor="text-secondary"
          bgColor="bg-secondary/10"
        />
        <SummaryCard 
          title="Pending Reviews" 
          value="18" 
          icon={<Clock className="w-5 h-5" />} 
          highlightColor="text-warning"
          bgColor="bg-warning/10"
        />
        <SummaryCard 
          title="Approved" 
          value="15" 
          icon={<CheckCircle2 className="w-5 h-5" />} 
          highlightColor="text-success"
          bgColor="bg-success/10"
        />
        <SummaryCard 
          title="Rejected" 
          value="4" 
          icon={<XCircle className="w-5 h-5" />} 
          highlightColor="text-text-secondary"
          bgColor="bg-background-muted"
        />
        <SummaryCard 
          title="High Risk" 
          value="5" 
          icon={<AlertTriangle className="w-5 h-5" />} 
          highlightColor="text-error"
          bgColor="bg-error/10"
        />
      </div>

      {/* Analytics Section */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
        <div className="lg:col-span-1">
          <ChartCard title="Portfolio Distribution">
            <ResponsiveContainer width="100%" height="100%">
              <RechartsPie>
                <Pie data={portfolioData} cx="50%" cy="50%" innerRadius={40} outerRadius={60} paddingAngle={2} dataKey="value">
                  {portfolioData.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                </Pie>
                <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #E5E7EB', fontSize: '12px' }} />
                <Legend iconType="circle" wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              </RechartsPie>
            </ResponsiveContainer>
          </ChartCard>
        </div>
        
        <div className="lg:col-span-1">
          <ChartCard title="Industry Spread">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={industryData} layout="vertical" margin={{ top: 0, right: 10, left: -20, bottom: 0 }}>
                <XAxis type="number" hide />
                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#6B7280' }} />
                <Tooltip cursor={{fill: '#F3F4F6'}} contentStyle={{ borderRadius: '8px', border: '1px solid #E5E7EB', fontSize: '12px' }} />
                <Bar dataKey="value" fill="#0F4C81" radius={[0, 4, 4, 0]} barSize={16} />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        <div className="lg:col-span-1">
          <ChartCard title="Risk Distribution">
            <ResponsiveContainer width="100%" height="100%">
              <RechartsPie>
                <Pie data={riskDistData} cx="50%" cy="50%" innerRadius={40} outerRadius={60} paddingAngle={2} dataKey="value">
                  {riskDistData.map((entry, index) => <Cell key={`cell-${index}`} fill={RISK_COLORS[index % RISK_COLORS.length]} />)}
                </Pie>
                <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #E5E7EB', fontSize: '12px' }} />
                <Legend iconType="circle" wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              </RechartsPie>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        <div className="lg:col-span-1">
          <div className="bg-primary border border-primary-hover rounded-card p-5 shadow-card flex flex-col h-full text-white">
            <h3 className="text-sm font-semibold text-white/90 mb-2">Overall Approval Rate</h3>
            <div className="flex-grow flex flex-col items-center justify-center">
              <div className="relative">
                <svg className="w-32 h-32 transform -rotate-90">
                  <circle cx="64" cy="64" r="56" stroke="currentColor" strokeWidth="12" fill="transparent" className="text-white/20" />
                  <circle cx="64" cy="64" r="56" stroke="currentColor" strokeWidth="12" fill="transparent" strokeDasharray="351.8" className="text-white" style={{ strokeDashoffset: 351.8 - (351.8 * 78) / 100 }} />
                </svg>
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-center">
                  <span className="text-3xl font-bold">78%</span>
                </div>
              </div>
              <p className="text-xs text-white/70 mt-4 text-center">AI pre-screening has improved approval velocity by 2.4x</p>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Section: Table & Alerts */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        
        {/* Application Queue Table */}
        <div className="xl:col-span-2 bg-white border border-border rounded-card shadow-card flex flex-col overflow-hidden">
          <div className="px-5 py-4 border-b border-border flex items-center justify-between bg-white">
            <h3 className="text-sm font-semibold text-text-primary">Application Queue</h3>
            <button className="text-xs font-medium text-primary hover:text-primary-hover">View Full Queue</button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-background-muted/50 border-b border-border">
                  <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Business</th>
                  <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Health</th>
                  <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Risk</th>
                  <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Requested</th>
                  <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Officer</th>
                  <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Status</th>
                  <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {tableData.map((row) => (
                  <tr key={row.id} className="hover:bg-background-muted/30 transition-colors">
                    <td className="px-5 py-3 align-middle">
                      <p className="text-sm font-semibold text-text-primary">{row.business}</p>
                      <p className="text-[10px] text-text-secondary">{row.id}</p>
                    </td>
                    <td className="px-5 py-3 align-middle text-sm font-medium text-text-primary">{row.score}</td>
                    <td className="px-5 py-3 align-middle"><RiskBadge risk={row.risk} /></td>
                    <td className="px-5 py-3 align-middle text-sm font-medium text-text-primary">{row.loan}</td>
                    <td className="px-5 py-3 align-middle text-sm text-text-secondary">{row.officer}</td>
                    <td className="px-5 py-3 align-middle"><StatusBadge status={row.status} /></td>
                    <td className="px-5 py-3 align-middle text-right">
                      <button className="inline-flex items-center justify-center w-8 h-8 rounded border border-border hover:bg-background-muted text-text-secondary transition-colors">
                        <Eye className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* AI Alerts Panel */}
        <div className="xl:col-span-1 bg-white border border-border rounded-card shadow-card flex flex-col overflow-hidden">
          <div className="px-5 py-4 border-b border-border flex items-center gap-2 bg-error/5">
            <BrainCircuit className="w-4 h-4 text-error" />
            <h3 className="text-sm font-semibold text-error">AI Underwriting Alerts</h3>
          </div>
          <div className="p-0 divide-y divide-border">
            
            <div className="p-4 hover:bg-background-muted/30 transition-colors flex items-start gap-3">
              <div className="mt-0.5"><AlertOctagon className="w-4 h-4 text-error" /></div>
              <div>
                <h4 className="text-sm font-semibold text-text-primary mb-1">High-Risk Business Flag</h4>
                <p className="text-xs text-text-secondary leading-relaxed mb-2">Global Logistics (APP-8923) exhibits severe liquidity constraints (Ratio: 0.8) and declining YoY revenue (-12%).</p>
                <button className="text-[11px] font-medium text-primary hover:underline">Review Financials</button>
              </div>
            </div>

            <div className="p-4 hover:bg-background-muted/30 transition-colors flex items-start gap-3">
              <div className="mt-0.5"><SearchCode className="w-4 h-4 text-warning" /></div>
              <div>
                <h4 className="text-sm font-semibold text-text-primary mb-1">GST vs Bank Inconsistency</h4>
                <p className="text-xs text-text-secondary leading-relaxed mb-2">Sunrise Retail (APP-8924) reported ₹1.2Cr in GSTR-1, but linked bank accounts show credit turnover of ₹85L.</p>
                <button className="text-[11px] font-medium text-primary hover:underline">View Reconciliation</button>
              </div>
            </div>

            <div className="p-4 hover:bg-background-muted/30 transition-colors flex items-start gap-3">
              <div className="mt-0.5"><FileWarning className="w-4 h-4 text-text-secondary" /></div>
              <div>
                <h4 className="text-sm font-semibold text-text-primary mb-1">Manual Review Recommended</h4>
                <p className="text-xs text-text-secondary leading-relaxed">Prime Manufacturing (APP-8925) machinery quotation exceeds standard market valuation by 18%. Needs physical verification.</p>
              </div>
            </div>

          </div>
        </div>

      </div>

    </div>
  );
}
