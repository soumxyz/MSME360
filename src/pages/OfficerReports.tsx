import React from 'react';
import { 
  Download, 
  FileSpreadsheet, 
  PieChart, 
  FileText, 
  CheckCircle2, 
  Clock, 
  Users
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  ResponsiveContainer,
  Tooltip,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';

const monthlyApprovalsData = [
  { name: 'Jan', approvals: 45, rejections: 12 },
  { name: 'Feb', approvals: 52, rejections: 15 },
  { name: 'Mar', approvals: 48, rejections: 18 },
  { name: 'Apr', approvals: 61, rejections: 14 },
  { name: 'May', approvals: 55, rejections: 20 },
  { name: 'Jun', approvals: 67, rejections: 16 },
];

const industryData = [
  { name: 'Manufacturing', value: 45 },
  { name: 'Retail', value: 25 },
  { name: 'IT Services', value: 20 },
  { name: 'Transportation', value: 10 },
];

const COLORS = ['#0F4C81', '#2563EB', '#60A5FA', '#93C5FD'];

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

export default function OfficerReports() {
  return (
    <div className="p-6 lg:p-8 w-full max-w-[1440px] mx-auto">
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary mb-1">Underwriting Analytics</h1>
          <p className="text-sm text-text-secondary">Platform metrics and officer performance reporting.</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="bg-white border border-border hover:bg-background-muted text-text-primary px-4 py-2 rounded text-sm font-medium transition-colors flex items-center gap-2">
            <FileSpreadsheet className="w-4 h-4" /> Download Excel
          </button>
          <button className="bg-primary hover:bg-primary-hover text-white px-4 py-2 rounded text-sm font-medium transition-colors flex items-center gap-2">
            <Download className="w-4 h-4" /> Download PDF
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <SummaryCard 
          title="Applications Processed" 
          value="1,245" 
          icon={<FileText className="w-5 h-5" />} 
          colorClass="bg-primary/10 text-primary"
        />
        <SummaryCard 
          title="Overall Approval Rate" 
          value="78%" 
          icon={<CheckCircle2 className="w-5 h-5" />} 
          colorClass="bg-success/10 text-success"
        />
        <SummaryCard 
          title="Avg. Review Time" 
          value="1.2 Hrs" 
          icon={<Clock className="w-5 h-5" />} 
          colorClass="bg-warning/10 text-warning"
        />
        <SummaryCard 
          title="Manual Reviews" 
          value="452" 
          icon={<Users className="w-5 h-5" />} 
          colorClass="bg-background-muted text-text-secondary"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white border border-border rounded-card p-6 shadow-card">
          <h3 className="text-base font-semibold text-text-primary mb-6">Monthly Approvals vs Rejections</h3>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={monthlyApprovalsData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#6B7280' }} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#6B7280' }} />
                <Tooltip 
                  cursor={{ fill: '#F3F4F6' }}
                  contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #E5E7EB', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }} 
                />
                <Legend iconType="circle" wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                <Bar dataKey="approvals" name="Approved" fill="#16A34A" radius={[4, 4, 0, 0]} />
                <Bar dataKey="rejections" name="Rejected" fill="#DC2626" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white border border-border rounded-card p-6 shadow-card">
          <h3 className="text-base font-semibold text-text-primary mb-6">Industry Distribution</h3>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <RechartsPieChart>
                <Pie
                  data={industryData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {industryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #E5E7EB', fontSize: '12px' }} />
                <Legend iconType="circle" wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
              </RechartsPieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
    </div>
  );
}
