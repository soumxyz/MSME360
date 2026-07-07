import React, { useState, useMemo, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
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
  BrainCircuit,
  ArrowRight
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
import { usePortfolio } from '../lib/api/hooks';
import type { PortfolioRow } from '../lib/api/types';
import { formatINRCompact } from '../lib/format';
import { PageSkeleton } from '../components/Skeleton';
import { BRAND, CHART_SERIES, RISK_SERIES, CHART_TOOLTIP_STYLE, AXIS_TICK_SM } from '../lib/palette';

const containerVariants: any = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.05 }
  }
};

const itemVariants: any = {
  hidden: { opacity: 0, y: 15 },
  show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 100, damping: 15 } }
};

const SummaryCard = ({ title, value, icon, highlightColor = 'text-primary', bgColor = 'bg-primary/10' }: any) => (
  <motion.div 
    variants={itemVariants}
    whileHover={{ y: -3, boxShadow: "0 12px 20px -8px rgba(15, 76, 129, 0.15)" }}
    className="bg-white border border-border rounded-card p-5 shadow-sm flex items-center justify-between transition-all duration-300"
  >
    <div>
      <p className="text-xs font-semibold text-text-secondary mb-1 uppercase tracking-wider">{title}</p>
      <h3 className="text-2xl font-bold text-text-primary">{value}</h3>
    </div>
    <div className={`p-3 rounded ${bgColor} ${highlightColor}`}>
      {icon}
    </div>
  </motion.div>
);

const ChartCard = ({ title, children }: { title: string, children: React.ReactNode }) => (
  <motion.div 
    variants={itemVariants}
    whileHover={{ y: -2 }}
    className="bg-white border border-border rounded-card p-5 shadow-card flex flex-col h-full transition-all duration-300 hover:border-primary/30"
  >
    <h3 className="text-sm font-semibold text-text-primary mb-4 uppercase tracking-wider">{title}</h3>
    <div className="flex-grow w-full h-[200px]">
      {children}
    </div>
  </motion.div>
);

const StatusBadge = ({ status }: { status: string }) => {
  if (status === 'Approved') return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-success/10 text-success border border-success/20">Approved</span>;
  if (status === 'Rejected') return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-error/10 text-error border border-error/20">Rejected</span>;
  if (status === 'Conditional') return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-secondary/10 text-secondary border border-secondary/20">Conditional</span>;
  return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-warning/10 text-warning border border-warning/20">Pending</span>;
};

const RiskBadge = ({ risk }: { risk: string }) => {
  if (risk === 'High') return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-error/10 text-error border border-error/20">High</span>;
  if (risk === 'Medium') return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-warning/10 text-warning border border-warning/20">Medium</span>;
  return <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-success/10 text-success border border-success/20">Low</span>;
};

export default function OfficerDashboard() {
  const { data, isLoading, error } = usePortfolio();
  const portfolioRows = (data || []) as PortfolioRow[];

  // --- Filter and Search States (search seeds from the topbar's ?q= param) ---
  const [searchParams] = useSearchParams();
  const [searchTerm, setSearchTerm] = useState(searchParams.get('q') ?? '');
  const [bandFilter, setBandFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [industryFilter, setIndustryFilter] = useState('');

  useEffect(() => {
    const q = searchParams.get('q');
    if (q !== null) setSearchTerm(q);
  }, [searchParams]);

  // --- Unique Industries list for dropdown ---
  const industries = useMemo(() => {
    return Array.from(new Set(portfolioRows.map((r: PortfolioRow) => r.industry))).sort();
  }, [portfolioRows]);

  // --- Filter and Search logic ---
  const filteredRows = useMemo(() => {
    return portfolioRows.filter((r: PortfolioRow) => {
      const matchesSearch = r.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                            r.business_id.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesBand = !bandFilter || r.band === bandFilter;
      const matchesStatus = !statusFilter || r.officer_status === statusFilter;
      const matchesIndustry = !industryFilter || r.industry === industryFilter;
      return matchesSearch && matchesBand && matchesStatus && matchesIndustry;
    });
  }, [portfolioRows, searchTerm, bandFilter, statusFilter, industryFilter]);

  if (isLoading) {
    return <PageSkeleton label="Loading portfolio data" />;
  }

  if (error || !data) {
    return (
      <div className="p-6 text-center text-error">
        <p className="font-semibold">Error loading portfolio</p>
        <p className="text-xs mt-1">Make sure the FastAPI server is running on port 8000.</p>
      </div>
    );
  }

  // --- Dynamic Stats Computations ---
  const totalApps = portfolioRows.length;
  const avgScore = Math.round(portfolioRows.reduce((acc: number, curr: PortfolioRow) => acc + curr.score, 0) / (totalApps || 1));
  const pendingCount = portfolioRows.filter((r: PortfolioRow) => r.officer_status === 'Pending').length;
  const approvedCount = portfolioRows.filter((r: PortfolioRow) => r.officer_status === 'Approved').length;
  const rejectedCount = portfolioRows.filter((r: PortfolioRow) => r.officer_status === 'Rejected').length;
  const highRiskCount = portfolioRows.filter((r: PortfolioRow) => r.band === 'High').length;

  // --- Risk Distribution Chart Data ---
  const riskDistData = [
    { name: 'Low Risk', value: portfolioRows.filter((r: PortfolioRow) => r.band === 'Low').length },
    { name: 'Medium Risk', value: portfolioRows.filter((r: PortfolioRow) => r.band === 'Medium').length },
    { name: 'High Risk', value: portfolioRows.filter((r: PortfolioRow) => r.band === 'High').length },
  ];

  // --- Industry Spread Chart Data ---
  const indMap: Record<string, number> = {};
  portfolioRows.forEach((r: PortfolioRow) => {
    indMap[r.industry] = (indMap[r.industry] || 0) + 1;
  });
  const industryData = Object.entries(indMap).map(([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value);

  // --- Portfolio Loan Distribution Chart Data ---
  const portfolioData = [
    { name: 'Working Capital', value: 45 },
    { name: 'Term Loans', value: 30 },
    { name: 'Machinery', value: 15 },
    { name: 'Vehicle', value: 10 },
  ];

  // --- Overall Approval Rate ---
  const approvalRate = totalApps > 0 ? Math.round(((approvedCount + portfolioRows.filter((r: PortfolioRow) => r.officer_status === 'Conditional').length) / totalApps) * 100) : 0;

  // --- Display filtered applications in table queue ---
  const tableRows = filteredRows;

  // --- AI alerts: surface the three weakest businesses in the live portfolio ---
  const alertRows = [...portfolioRows].sort((a, b) => a.score - b.score).slice(0, 3);
  const ALERT_META = [
    { icon: <AlertOctagon className="w-4 h-4 text-error" aria-hidden="true" />, title: 'High-Risk Business Flag', cta: 'Review Financials' },
    { icon: <SearchCode className="w-4 h-4 text-warning" aria-hidden="true" />, title: 'Weak Cash Flow Signals', cta: 'View Reconciliation' },
    { icon: <FileWarning className="w-4 h-4 text-text-secondary" aria-hidden="true" />, title: 'Manual Review Recommended', cta: 'Review Trends' },
  ];

  return (
    <motion.div 
      initial="hidden"
      animate="show"
      variants={containerVariants}
      className="p-6 lg:p-8 w-full mx-auto"
    >
      {/* Page Header */}
      <div className="mb-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-border pb-5">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Officer Command Center</h1>
          <p className="text-sm text-text-secondary mt-1">Real-time alternate data credit scoring, risk profiling, and decisioning queue.</p>
        </div>
        <Link 
          to="/register" 
          className="inline-flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-semibold rounded shadow-sm transition-colors cursor-pointer self-start sm:self-center"
        >
          <FileCheck className="w-4.5 h-4.5" /> New Intake Check
        </Link>
      </div>
      
      {/* Summary Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4 mb-6">
        <SummaryCard 
          title="Total Applications" 
          value={totalApps} 
          icon={<FileCheck className="w-5 h-5" />} 
        />
        <SummaryCard 
          title="Avg Health Score" 
          value={avgScore} 
          icon={<Activity className="w-5 h-5" />} 
          highlightColor="text-secondary"
          bgColor="bg-secondary/10"
        />
        <SummaryCard 
          title="Pending Reviews" 
          value={pendingCount} 
          icon={<Clock className="w-5 h-5" />} 
          highlightColor="text-warning"
          bgColor="bg-warning/10"
        />
        <SummaryCard 
          title="Approved" 
          value={approvedCount} 
          icon={<CheckCircle2 className="w-5 h-5" />} 
          highlightColor="text-success"
          bgColor="bg-success/10"
        />
        <SummaryCard 
          title="Rejected" 
          value={rejectedCount} 
          icon={<XCircle className="w-5 h-5" />} 
          highlightColor="text-text-secondary"
          bgColor="bg-background-muted"
        />
        <SummaryCard 
          title="High Risk" 
          value={highRiskCount} 
          icon={<AlertTriangle className="w-5 h-5" />} 
          highlightColor="text-error"
          bgColor="bg-error/10"
        />
      </div>


      {/* Analytics Section */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
        <div className="lg:col-span-1">
          <ChartCard title="Portfolio Distribution">
            <ResponsiveContainer width="100%" height={200}>
              <RechartsPie>
                <Pie data={portfolioData} cx="50%" cy="50%" innerRadius={40} outerRadius={60} paddingAngle={2} dataKey="value">
                  {portfolioData.map((entry, index) => <Cell key={`cell-${index}`} fill={CHART_SERIES[index % CHART_SERIES.length]} />)}
                </Pie>
                <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                <Legend iconType="circle" wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              </RechartsPie>
            </ResponsiveContainer>
          </ChartCard>
        </div>
        
        <div className="lg:col-span-1">
          <ChartCard title="Industry Spread">
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={industryData} layout="vertical" margin={{ top: 0, right: 10, left: -20, bottom: 0 }}>
                <XAxis type="number" hide />
                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={AXIS_TICK_SM} />
                <Tooltip cursor={{ fill: BRAND.surfaceMuted }} contentStyle={CHART_TOOLTIP_STYLE} />
                <Bar dataKey="value" fill={BRAND.primary} radius={[0, 4, 4, 0]} barSize={16} />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        <div className="lg:col-span-1">
          <ChartCard title="Risk Distribution">
            <ResponsiveContainer width="100%" height={200}>
              <RechartsPie>
                <Pie data={riskDistData} cx="50%" cy="50%" innerRadius={40} outerRadius={60} paddingAngle={2} dataKey="value">
                  {riskDistData.map((entry, index) => <Cell key={`cell-${index}`} fill={RISK_SERIES[index % RISK_SERIES.length]} />)}
                </Pie>
                <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                <Legend iconType="circle" wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              </RechartsPie>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        <motion.div variants={itemVariants} className="lg:col-span-1">
          <div className="bg-primary border border-primary-hover rounded-card p-5 shadow-card flex flex-col h-full text-white">
            <h3 className="text-sm font-semibold text-white/90 mb-2">Overall Approval Rate</h3>
            <div className="flex-grow flex flex-col items-center justify-center">
              <div className="relative">
                <svg className="w-32 h-32 transform -rotate-90">
                  <circle cx="64" cy="64" r="56" stroke="currentColor" strokeWidth="12" fill="transparent" className="text-white/20" />
                  <circle cx="64" cy="64" r="56" stroke="currentColor" strokeWidth="12" fill="transparent" strokeDasharray="351.8" className="text-white" style={{ strokeDashoffset: 351.8 - (351.8 * (approvalRate || 1)) / 100 }} />
                </svg>
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-center">
                  <span className="text-3xl font-bold">{approvalRate}%</span>
                </div>
              </div>
              <p className="text-xs text-white/70 mt-4 text-center">AI pre-screening has improved approval velocity by 2.4x</p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Bottom Section: Table & Alerts */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        
        <motion.div variants={itemVariants} className="xl:col-span-2 bg-white border border-border rounded-card shadow-card flex flex-col overflow-hidden">
          <div className="px-5 py-4 border-b border-border bg-white space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-text-primary">Application Queue</h3>
              <div className="flex items-center gap-3">
                {Boolean(searchTerm || bandFilter || statusFilter || industryFilter) && (
                  <button 
                    onClick={() => {
                      setSearchTerm('');
                      setBandFilter('');
                      setStatusFilter('');
                      setIndustryFilter('');
                    }}
                    className="text-xs text-text-secondary hover:text-text-primary underline cursor-pointer"
                  >
                    Clear Filters
                  </button>
                )}
                <span className="text-xs text-text-secondary">Showing {filteredRows.length} entries</span>
              </div>
            </div>
            
            {/* Filter Toolbar */}
            <div className="flex flex-wrap items-center gap-3 pt-2">
              <input
                type="search"
                placeholder="Search business..."
                aria-label="Search businesses in the application queue"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="px-3 py-1.5 border border-border rounded text-xs focus:outline-none focus:border-primary flex-grow sm:flex-grow-0 sm:w-44"
              />
              <select 
                value={bandFilter}
                onChange={(e) => setBandFilter(e.target.value)}
                className="border border-border rounded px-2.5 py-1.5 text-xs text-text-primary focus:outline-none focus:border-primary cursor-pointer bg-white"
              >
                <option value="">All Risk Bands</option>
                <option value="Low">Low Risk</option>
                <option value="Medium">Medium Risk</option>
                <option value="High">High Risk</option>
              </select>
              <select 
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="border border-border rounded px-2.5 py-1.5 text-xs text-text-primary focus:outline-none focus:border-primary cursor-pointer bg-white"
              >
                <option value="">All Statuses</option>
                <option value="Pending">Pending</option>
                <option value="Approved">Approved</option>
                <option value="Rejected">Rejected</option>
                <option value="Conditional">Conditional</option>
              </select>
              <select 
                value={industryFilter}
                onChange={(e) => setIndustryFilter(e.target.value)}
                className="border border-border rounded px-2.5 py-1.5 text-xs text-text-primary focus:outline-none focus:border-primary cursor-pointer bg-white w-36"
              >
                <option value="">All Industries</option>
                {industries.map(ind => (
                  <option key={ind} value={ind}>{ind}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-background-muted/50 border-b border-border">
                  <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Business</th>
                  <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Health</th>
                  <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Risk</th>
                  <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Requested</th>
                  <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider">Status</th>
                  <th className="px-5 py-3 text-xs font-semibold text-text-secondary uppercase tracking-wider text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {tableRows.map((row) => (
                  <tr key={row.business_id} className="hover:bg-background-muted/30 transition-colors">
                    <td className="px-5 py-3 align-middle">
                      <p className="text-sm font-semibold text-text-primary">{row.name}</p>
                      <p className="text-[10px] text-text-secondary">{row.business_id} • {row.industry}</p>
                    </td>
                    <td className="px-5 py-3 align-middle text-sm font-semibold text-text-primary tnum">{row.score}</td>
                    <td className="px-5 py-3 align-middle"><RiskBadge risk={row.band} /></td>
                    <td className="px-5 py-3 align-middle text-sm font-medium text-text-primary tnum">
                      {formatINRCompact(row.avg_monthly_revenue * 3)}
                    </td>
                    <td className="px-5 py-3 align-middle"><StatusBadge status={row.officer_status} /></td>
                    <td className="px-5 py-3 align-middle text-right">
                      <Link
                        to={`/officer/applications/${row.business_id}`}
                        aria-label={`Review ${row.name}`}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-[#008269]/10 hover:bg-[#008269] text-[#008269] hover:text-white text-xs font-bold border border-[#008269]/20 transition-all cursor-pointer shadow-xs"
                      >
                        <BrainCircuit className="w-3.5 h-3.5" />
                        Underwrite
                      </Link>
                    </td>
                  </tr>
                ))}
                {tableRows.length === 0 && (
                  <tr>
                    <td colSpan={6} className="px-5 py-10 text-center">
                      <p className="text-sm font-medium text-text-primary mb-1">No applications match these filters</p>
                      <p className="text-xs text-text-secondary">Try a different search term, or use “Clear Filters” above to reset the queue.</p>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </motion.div>

        {/* AI Alerts Panel */}
        <motion.div variants={itemVariants} className="xl:col-span-1 bg-white border border-border rounded-card shadow-card flex flex-col overflow-hidden">
          <div className="px-5 py-4 border-b border-border flex items-center gap-2 bg-error/5">
            <BrainCircuit className="w-4 h-4 text-error" />
            <h3 className="text-sm font-semibold text-error">AI Underwriting Alerts</h3>
          </div>
          <div className="p-0 divide-y divide-border">
            {alertRows.map((biz, i) => (
              <div key={biz.business_id} className="p-4 hover:bg-background-muted/30 transition-colors flex items-start gap-3">
                <div className="mt-0.5">{ALERT_META[i].icon}</div>
                <div>
                  <h4 className="text-sm font-semibold text-text-primary mb-1">{ALERT_META[i].title}</h4>
                  <p className="text-xs text-text-secondary leading-relaxed mb-2">
                    {biz.name} ({biz.business_id}) scored <span className="tnum font-semibold">{biz.score}/100</span> — {biz.band} risk band, flagged by the Agent 2 scoring model for officer review.
                  </p>
                  <Link to={`/officer/applications/${biz.business_id}`} className="text-[11px] font-medium text-primary hover:underline">
                    {ALERT_META[i].cta}
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

      </div>



    </motion.div>
  );
}
