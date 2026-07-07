import React from 'react';
import { 
  TrendingUp, 
  AlertTriangle,
  BrainCircuit,
  Search,
  CheckCircle2,
  Lightbulb
} from 'lucide-react';
import { 
  AreaChart,
  Area,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend
} from 'recharts';

// --- Mock Data ---
const healthTrendData = [
  { month: 'Jan', healthScore: 75 },
  { month: 'Feb', healthScore: 72 },
  { month: 'Mar', healthScore: 78 },
  { month: 'Apr', healthScore: 65 },
  { month: 'May', healthScore: 70 },
  { month: 'Jun', healthScore: 82 }, 
];

const healthDistributionData = [
  { name: 'Cash Flow Health', value: 45 },
  { name: 'Business Stability', value: 25 },
  { name: 'Business Growth Outlook', value: 20 },
  { name: 'Compliance Health', value: 10 },
];

const COLORS = ['#0F4C81', '#2563EB', '#60A5FA', '#93C5FD'];

const insights = [
  { 
    id: 1, 
    category: 'Cash Flow Health', 
    factor: 'Customer Payments', 
    status: 'Needs Attention', 
    observation: 'Payments from customers are taking longer than usual.',
    impact: 'Average collection period increased to 65 days, reducing your short-term available cash.',
    suggestion: 'Improving collection cycles can strengthen your business and increase loan eligibility.' 
  },
  { 
    id: 2, 
    category: 'Compliance Health', 
    factor: 'GST Filing', 
    status: 'Excellent', 
    observation: 'Consistent on-time GST filings.',
    impact: '100% on-time filing over the last 12 months demonstrates strong financial discipline.',
    suggestion: 'Continue current practices to maintain high business credibility.' 
  },
  { 
    id: 3, 
    category: 'Business Stability', 
    factor: 'Client Base Diversity', 
    status: 'Needs Attention', 
    observation: 'High reliance on a small number of clients.',
    impact: 'Top 2 clients account for 68% of total revenue. Losing either could impact your cash flow.',
    suggestion: 'Diversifying your client base will make your revenue streams more resilient.' 
  },
  { 
    id: 4, 
    category: 'Business Growth Outlook', 
    factor: 'Industry Expansion', 
    status: 'Good', 
    observation: 'Operating in a growing sector.',
    impact: 'Manufacturing sector is showing a steady 8% YoY growth, creating a favorable business environment.',
    suggestion: 'Leverage industry growth to negotiate better terms with suppliers.' 
  }
];

export default function BusinessInsights() {
  return (
    <div className="p-6 lg:p-8 w-full max-w-[1440px] mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-text-primary mb-1">Business Insights</h1>
        <p className="text-sm text-text-secondary">Understand the factors influencing your financial health score.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="md:col-span-2 bg-white border border-border rounded-card p-6 shadow-card">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-base font-semibold text-text-primary">Financial Health History</h3>
              <p className="text-xs text-text-secondary">Historical composite score (higher is better)</p>
            </div>
            <div className="flex items-center gap-2 px-3 py-1 bg-success/10 text-success rounded text-sm font-medium">
              <TrendingUp className="w-4 h-4" /> 
              Improving
            </div>
          </div>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={healthTrendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorHealth" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0F4C81" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#0F4C81" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#6B7280' }} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#6B7280' }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #E5E7EB', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }} 
                />
                <Area type="monotone" dataKey="healthScore" stroke="#0F4C81" strokeWidth={3} fillOpacity={1} fill="url(#colorHealth)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white border border-border rounded-card p-6 shadow-card">
          <h3 className="text-base font-semibold text-text-primary mb-2">Category Breakdown</h3>
          <p className="text-xs text-text-secondary mb-4">Areas affecting your score</p>
          <div className="h-[220px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={healthDistributionData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {healthDistributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #E5E7EB', fontSize: '12px' }} />
                <Legend iconType="circle" wrapperStyle={{ fontSize: '12px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white border border-border rounded-card shadow-card overflow-hidden">
          <div className="p-5 border-b border-border flex items-center justify-between bg-background-muted/30">
            <h3 className="text-base font-semibold text-text-primary">Key Business Observations</h3>
            <div className="relative">
              <Search className="w-4 h-4 text-text-secondary absolute left-3 top-1/2 -translate-y-1/2" />
              <input 
                type="text" 
                placeholder="Search insights..." 
                className="pl-9 pr-4 py-1.5 border border-border rounded text-sm focus:outline-none focus:border-primary w-48"
              />
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-border bg-white">
                  <th className="px-5 py-3 text-xs font-medium text-text-secondary uppercase tracking-wider">Category</th>
                  <th className="px-5 py-3 text-xs font-medium text-text-secondary uppercase tracking-wider">Observation</th>
                  <th className="px-5 py-3 text-xs font-medium text-text-secondary uppercase tracking-wider">Status</th>
                  <th className="px-5 py-3 text-xs font-medium text-text-secondary uppercase tracking-wider">Business Impact & Suggestion</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {insights.map((row) => (
                  <tr key={row.id} className="hover:bg-background-muted/50 transition-colors">
                    <td className="px-5 py-4 text-sm text-text-primary">{row.category}</td>
                    <td className="px-5 py-4 text-sm font-medium text-text-primary">{row.factor}</td>
                    <td className="px-5 py-4">
                      {row.status === 'Needs Attention' && <span className="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium bg-warning/10 text-warning">{row.status}</span>}
                      {row.status === 'Good' && <span className="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium bg-primary/10 text-primary">{row.status}</span>}
                      {row.status === 'Excellent' && <span className="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium bg-success/10 text-success">{row.status}</span>}
                    </td>
                    <td className="px-5 py-4">
                      <p className="text-sm text-text-primary mb-1">{row.observation}</p>
                      <p className="text-xs text-text-secondary mb-1">{row.impact}</p>
                      <p className="text-xs text-primary font-medium">{row.suggestion}</p>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="lg:col-span-1 bg-primary/5 border border-primary/20 rounded-card p-6 shadow-sm flex flex-col">
          <div className="flex items-center gap-2 mb-6 border-b border-primary/20 pb-4">
            <Lightbulb className="w-5 h-5 text-primary" />
            <h3 className="text-base font-semibold text-text-primary">Insight Explanation Panel</h3>
          </div>
          <div className="flex-grow space-y-6">
            <div>
              <h4 className="text-sm font-bold text-text-primary mb-2 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-warning" /> High Client Concentration
              </h4>
              <p className="text-sm text-text-secondary leading-relaxed mb-3">
                <strong className="text-text-primary block mb-1">Why AI detected it:</strong>
                Based on your connected GST returns, 68% of your revenue originates from just two clients.
              </p>
              <p className="text-sm text-text-secondary leading-relaxed mb-3">
                <strong className="text-text-primary block mb-1">What this means for your business:</strong>
                Relying heavily on a few clients can impact your Business Stability score because unexpected delays from those clients could severely disrupt your cash flow.
              </p>
            </div>
            <div>
              <h4 className="text-sm font-bold text-text-primary mb-2 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-success" /> Mitigating Factors Detected
              </h4>
              <p className="text-sm text-text-secondary leading-relaxed">
                Your bank statements show that these top clients have consistently paid within 15 days over the past 24 months, which significantly strengthens your overall financial profile despite the concentration.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
