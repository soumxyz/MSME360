import React from 'react';
import { 
  Activity, 
  ArrowRight,
  TrendingUp,
  BrainCircuit,
  Building2,
  AlertTriangle,
  CheckCircle2,
  Download,
  Banknote,
  ShieldCheck,
  FileText,
  Smartphone,
  Landmark,
  Briefcase,
  ScrollText,
  FileStack
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Tooltip
} from 'recharts';
import { Link } from 'react-router-dom';

const radarData = [
  { subject: 'Cash Flow', A: 85, fullMark: 100 },
  { subject: 'Revenue Growth', A: 78, fullMark: 100 },
  { subject: 'GST Compliance', A: 95, fullMark: 100 },
  { subject: 'Digital Payments', A: 82, fullMark: 100 },
  { subject: 'Business Stability', A: 70, fullMark: 100 },
];

const barData = [
  { name: 'Jan', revenue: 45, expense: 38 },
  { name: 'Feb', revenue: 52, expense: 41 },
  { name: 'Mar', revenue: 48, expense: 43 },
  { name: 'Apr', revenue: 61, expense: 45 },
  { name: 'May', revenue: 55, expense: 42 },
  { name: 'Jun', revenue: 67, expense: 48 },
];

const SummaryCard = ({ title, value, icon, trend, trendLabel, subStatus }: any) => (
  <div className="bg-white border border-border rounded-card p-5 shadow-card flex flex-col h-full">
    <div className="flex items-center justify-between mb-4">
      <h3 className="text-sm font-semibold text-text-secondary">{title}</h3>
      <div className="p-2 bg-background-muted rounded text-primary">
        {icon}
      </div>
    </div>
    <div className="mb-2">
      <span className="text-2xl font-bold text-text-primary">{value}</span>
    </div>
    <div className="flex items-center gap-2 mt-auto">
      {subStatus ? (
        <span className="inline-flex items-center gap-1 text-xs font-medium text-success bg-success/10 px-2 py-0.5 rounded border border-success/20">
          {subStatus}
        </span>
      ) : trend === 'up' ? (
        <span className="inline-flex items-center gap-1 text-xs font-medium text-success bg-success/10 px-2 py-0.5 rounded border border-success/20">
          <TrendingUp className="w-3 h-3" /> +12.5%
        </span>
      ) : (
        <span className="inline-flex items-center gap-1 text-xs font-medium text-warning bg-warning/10 px-2 py-0.5 rounded border border-warning/20">
          <AlertTriangle className="w-3 h-3" /> Needs Attention
        </span>
      )}
      {trendLabel && <span className="text-xs text-text-secondary">{trendLabel}</span>}
    </div>
  </div>
);

export default function CustomerDashboard() {
  return (
    <div className="p-6 lg:p-8 w-full max-w-[1440px] mx-auto">
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary mb-1">Financial Health Overview</h1>
          <p className="text-sm text-text-secondary">AI-driven analysis based on your connected integrations.</p>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/customer/reports" className="bg-white border border-border hover:bg-background-muted text-text-primary px-4 py-2 rounded text-sm font-medium transition-colors flex items-center gap-2">
            <Download className="w-4 h-4" /> Download Report
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <SummaryCard 
          title="Overall Health Score" 
          value="82/100" 
          icon={<Activity className="w-5 h-5" />} 
          trend="up" 
          trendLabel="vs last quarter"
        />
        <SummaryCard 
          title="Eligible Loan Amount" 
          value="₹45 Lakhs" 
          icon={<Banknote className="w-5 h-5" />} 
          subStatus="Pre-qualified"
        />
        <SummaryCard 
          title="Business Grade" 
          value="A-" 
          icon={<ShieldCheck className="w-5 h-5" />} 
          trend="up"
          trendLabel="Top 15% among Manufacturing MSMEs"
        />
        <SummaryCard 
          title="Compliance Status" 
          value="Excellent" 
          icon={<CheckCircle2 className="w-5 h-5 text-success" />} 
          trend="up" 
          trendLabel="100% on-time GST"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2 bg-white border border-border rounded-card p-6 shadow-card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-base font-semibold text-text-primary">Revenue vs Expense Trend (Last 6 Months)</h3>
          </div>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#6B7280' }} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#6B7280' }} />
                <Tooltip 
                  cursor={{ fill: '#F3F4F6' }}
                  contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #E5E7EB', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }} 
                />
                <Bar dataKey="revenue" name="Revenue (Lakhs)" fill="#0F4C81" radius={[4, 4, 0, 0]} />
                <Bar dataKey="expense" name="Expense (Lakhs)" fill="#60A5FA" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="lg:col-span-1 bg-white border border-border rounded-card p-6 shadow-card flex flex-col">
          <h3 className="text-base font-semibold text-text-primary mb-2">Category Performance</h3>
          <div className="flex-grow min-h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                <PolarGrid stroke="#E5E7EB" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#6B7280', fontSize: 11 }} />
                <Radar name="Score" dataKey="A" stroke="#0F4C81" fill="#0F4C81" fillOpacity={0.2} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* AI Business Summary & Confidence */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2 bg-primary/5 border border-primary/20 rounded-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <BrainCircuit className="w-5 h-5 text-primary" />
            <h3 className="text-base font-semibold text-text-primary">AI Business Summary</h3>
          </div>
          
          <div className="mb-6">
            <h4 className="text-sm font-semibold text-text-primary mb-2">Executive Summary</h4>
            <p className="text-sm text-text-secondary leading-relaxed">
              Revenue has increased consistently over the past year. GST compliance is excellent. Digital transactions indicate stable business activity.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <h4 className="text-sm font-semibold text-text-primary mb-2">Business Strengths</h4>
              <ul className="space-y-2">
                <li className="flex items-start gap-2 text-sm text-text-secondary">
                  <CheckCircle2 className="w-4 h-4 text-success mt-0.5 flex-shrink-0" />
                  Consistent YoY revenue growth.
                </li>
                <li className="flex items-start gap-2 text-sm text-text-secondary">
                  <CheckCircle2 className="w-4 h-4 text-success mt-0.5 flex-shrink-0" />
                  Flawless statutory GST compliance.
                </li>
              </ul>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-text-primary mb-2">Areas for Improvement</h4>
              <ul className="space-y-2">
                <li className="flex items-start gap-2 text-sm text-text-secondary">
                  <AlertTriangle className="w-4 h-4 text-warning mt-0.5 flex-shrink-0" />
                  High customer concentration.
                </li>
              </ul>
            </div>
          </div>
          
          <div className="bg-white border border-border p-4 rounded">
            <h4 className="text-sm font-semibold text-text-primary mb-1">Recommended Next Action</h4>
            <p className="text-sm text-text-secondary leading-relaxed">
              Reducing customer concentration can improve your financial health score and unlock higher credit limits.
            </p>
          </div>
        </div>

        <div className="lg:col-span-1 bg-white border border-border rounded-card p-6 shadow-card">
          <h3 className="text-base font-semibold text-text-primary mb-1">Assessment Confidence</h3>
          <p className="text-xs text-text-secondary mb-6">Based on connected alternate data sources</p>
          
          <div className="flex items-center justify-center mb-8">
            <div className="w-32 h-32 rounded-full border-[10px] border-success/20 border-t-success flex items-center justify-center">
              <span className="text-3xl font-bold text-success">96%</span>
            </div>
          </div>

          <div className="space-y-3">
            <p className="text-xs font-semibold text-text-primary mb-2">Assessment generated using:</p>
            <div className="flex items-center gap-2 text-sm text-text-secondary">
              <CheckCircle2 className="w-4 h-4 text-success" /> GST Returns
            </div>
            <div className="flex items-center gap-2 text-sm text-text-secondary">
              <CheckCircle2 className="w-4 h-4 text-success" /> UPI Transactions
            </div>
            <div className="flex items-center gap-2 text-sm text-text-secondary">
              <CheckCircle2 className="w-4 h-4 text-success" /> Account Aggregator
            </div>
            <div className="flex items-center gap-2 text-sm text-text-secondary">
              <CheckCircle2 className="w-4 h-4 text-success" /> EPFO Records
            </div>
            <div className="flex items-center gap-2 text-sm text-text-secondary">
              <CheckCircle2 className="w-4 h-4 text-success" /> Bank Statements
            </div>
            <div className="flex items-center gap-2 text-sm text-text-secondary">
              <CheckCircle2 className="w-4 h-4 text-success" /> Sales Invoices
            </div>
          </div>
        </div>
      </div>

      {/* Next Step Section */}
      <div className="bg-white border border-border rounded-card p-8 shadow-card text-center mb-8">
        <h2 className="text-xl font-semibold text-text-primary mb-2">Next Step</h2>
        <p className="text-text-secondary mb-6 max-w-lg mx-auto">
          Your business qualifies for financing based on your outstanding financial health score. 
          Explore pre-qualified credit facilities mapped specifically to your operational needs.
        </p>
        <Link to="/customer/loans" className="inline-flex items-center gap-2 bg-primary hover:bg-primary-hover text-white px-8 py-3 rounded font-medium transition-colors">
          Explore Loan Offers <ArrowRight className="w-5 h-5" />
        </Link>
      </div>

    </div>
  );
}
