import React from 'react';
import { 
  Activity, 
  Download, 
  Printer, 
  Share2, 
  CheckCircle2,
  AlertTriangle,
  QrCode,
  ShieldCheck,
  ArrowLeft,
  Smartphone,
  Landmark,
  Briefcase,
  ScrollText,
  FileStack,
  FileText,
  Banknote
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  ResponsiveContainer,
  LineChart,
  Line,
  LabelList
} from 'recharts';
import { Link } from 'react-router-dom';

const categoryScores = [
  { name: 'Cash Flow', score: 85 },
  { name: 'GST Compliance', score: 95 },
  { name: 'Growth', score: 78 },
  { name: 'Digital Payments', score: 82 },
  { name: 'Business Stability', score: 70 },
];

const revenueTrend = [
  { month: 'Jan', revenue: 45, expense: 38 },
  { month: 'Feb', revenue: 52, expense: 41 },
  { month: 'Mar', revenue: 48, expense: 43 },
  { month: 'Apr', revenue: 61, expense: 45 },
  { month: 'May', revenue: 55, expense: 42 },
  { month: 'Jun', revenue: 67, expense: 48 },
];

const ReportHeader = () => (
  <div className="flex items-center justify-between border-b-2 border-primary pb-6 mb-8">
    <div className="flex items-center gap-3">
      <div className="w-10 h-10 bg-primary rounded flex items-center justify-center">
        <Activity className="w-6 h-6 text-white" />
      </div>
      <div>
        <h1 className="text-xl font-bold text-primary tracking-tight uppercase">IDBI Bank</h1>
        <p className="text-[10px] text-text-secondary tracking-widest uppercase">MSME Assessment Portal</p>
      </div>
    </div>
    <div className="text-right">
      <h2 className="text-lg font-semibold text-text-primary">Financial Health Report</h2>
      <p className="text-xs text-text-secondary">Ref No: IDBI/FHR/2026/07-9482</p>
      <p className="text-xs text-text-secondary">Date: {new Date().toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}</p>
    </div>
  </div>
);

const SectionTitle = ({ title }: { title: string }) => (
  <h3 className="text-sm font-bold text-text-primary uppercase tracking-wider mb-4 border-b border-border pb-1">{title}</h3>
);

const BusinessInfo = () => (
  <div className="mb-8">
    <SectionTitle title="Business Information" />
    <div className="grid grid-cols-2 gap-y-4 gap-x-8 text-sm">
      <div className="flex justify-between">
        <span className="text-text-secondary">Entity Name:</span>
        <span className="font-semibold text-text-primary">Acme Industries Pvt Ltd</span>
      </div>
      <div className="flex justify-between">
        <span className="text-text-secondary">GSTIN:</span>
        <span className="font-medium text-text-primary">22AAAAA0000A1Z5</span>
      </div>
      <div className="flex justify-between">
        <span className="text-text-secondary">PAN:</span>
        <span className="font-medium text-text-primary">ABCDE1234F</span>
      </div>
      <div className="flex justify-between">
        <span className="text-text-secondary">Industry:</span>
        <span className="font-medium text-text-primary">Manufacturing</span>
      </div>
      <div className="flex justify-between">
        <span className="text-text-secondary">Vintage:</span>
        <span className="font-medium text-text-primary">5-10 Years</span>
      </div>
      <div className="flex justify-between">
        <span className="text-text-secondary">Assessment Confidence:</span>
        <span className="font-medium text-success">96%</span>
      </div>
    </div>
  </div>
);

const ScoresSection = () => (
  <div className="mb-8">
    <SectionTitle title="Health Assessment Scores" />
    <div className="grid grid-cols-3 gap-6 mb-6">
      <div className="p-4 bg-background-muted border border-border rounded text-center">
        <p className="text-xs text-text-secondary mb-1">Final Health Score</p>
        <p className="text-3xl font-bold text-success">82<span className="text-sm text-text-secondary font-normal">/100</span></p>
      </div>
      <div className="p-4 bg-background-muted border border-border rounded text-center">
        <p className="text-xs text-text-secondary mb-1">Business Grade</p>
        <p className="text-3xl font-bold text-text-primary">A-</p>
      </div>
      <div className="p-4 bg-background-muted border border-border rounded text-center">
        <p className="text-xs text-text-secondary mb-1">Risk Adjustment</p>
        <p className="text-xl font-bold text-text-primary mt-2">-4 Pts</p>
      </div>
    </div>
    
    <div>
      <h4 className="text-xs font-semibold text-text-secondary mb-3">Score Breakdown</h4>
      <div className="h-[180px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={categoryScores} layout="vertical" margin={{ top: 0, right: 30, left: 0, bottom: 0 }}>
            <XAxis type="number" domain={[0, 100]} hide />
            <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#6B7280' }} width={120} />
            <Bar dataKey="score" fill="#0F4C81" radius={[0, 4, 4, 0]} barSize={16}>
              <LabelList dataKey="score" position="right" style={{ fontSize: '11px', fill: '#111827', fontWeight: 600 }} />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  </div>
);

const DataSourcesSection = () => (
  <div className="mb-8">
    <SectionTitle title="Connected Data Sources" />
    <div className="grid grid-cols-3 gap-y-3">
      <div className="flex items-center gap-2 text-sm text-text-secondary">
        <CheckCircle2 className="w-4 h-4 text-success" /> <FileText className="w-3.5 h-3.5 opacity-50"/> GST
      </div>
      <div className="flex items-center gap-2 text-sm text-text-secondary">
        <CheckCircle2 className="w-4 h-4 text-success" /> <Smartphone className="w-3.5 h-3.5 opacity-50"/> UPI
      </div>
      <div className="flex items-center gap-2 text-sm text-text-secondary">
        <CheckCircle2 className="w-4 h-4 text-success" /> <Landmark className="w-3.5 h-3.5 opacity-50"/> AA
      </div>
      <div className="flex items-center gap-2 text-sm text-text-secondary">
        <CheckCircle2 className="w-4 h-4 text-success" /> <Briefcase className="w-3.5 h-3.5 opacity-50"/> EPFO
      </div>
      <div className="flex items-center gap-2 text-sm text-text-secondary">
        <CheckCircle2 className="w-4 h-4 text-success" /> <ScrollText className="w-3.5 h-3.5 opacity-50"/> Bank Statements
      </div>
      <div className="flex items-center gap-2 text-sm text-text-secondary">
        <CheckCircle2 className="w-4 h-4 text-success" /> <FileStack className="w-3.5 h-3.5 opacity-50"/> Sales Invoices
      </div>
    </div>
    <p className="text-[10px] text-text-secondary mt-3 italic">Data Completeness: 100% verified across 6 institutional sources.</p>
  </div>
);

const AIAnalysisSection = () => (
  <div className="mb-8">
    <SectionTitle title="AI Executive Summary" />
    <div className="space-y-4">
      <div className="border-l-2 border-primary pl-4">
        <p className="text-[11px] text-text-secondary leading-relaxed">
          Acme Industries Pvt Ltd demonstrates strong revenue growth (18% YoY) and excellent compliance records. 
          The primary vulnerability lies in working capital lock-up due to extended debtor cycles. The business is fundamentally sound and qualifies for institutional credit expansion.
        </p>
      </div>
      
      <div className="grid grid-cols-2 gap-6 pt-2">
        <div>
          <h4 className="text-xs font-bold text-text-primary mb-2 flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5 text-success" /> Business Strengths
          </h4>
          <ul className="space-y-1 text-[11px] text-text-secondary list-disc pl-4">
            <li>Consistent YoY revenue growth across 3 quarters.</li>
            <li>100% on-time GST filing history.</li>
            <li>Healthy transition to digital payments (82%).</li>
          </ul>
        </div>
        
        <div>
          <h4 className="text-xs font-bold text-text-primary mb-2 flex items-center gap-1">
            <AlertTriangle className="w-3.5 h-3.5 text-warning" /> Business Weaknesses
          </h4>
          <ul className="space-y-1 text-[11px] text-text-secondary list-disc pl-4">
            <li>Customer payment collection cycle has increased to 65 days.</li>
            <li>High reliance on top 2 clients (68% of revenue).</li>
          </ul>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6 pt-2">
        <div>
          <h4 className="text-xs font-bold text-text-primary mb-2 flex items-center gap-1">
            <Activity className="w-3.5 h-3.5 text-primary" /> Improvement Suggestions
          </h4>
          <ul className="space-y-1 text-[11px] text-text-secondary list-disc pl-4">
            <li>Implement invoice discounting to reduce debtor cycle.</li>
            <li>Diversify client base to spread revenue reliance.</li>
            <li><strong>Future Score Potential: 88/100</strong> (if addressed)</li>
          </ul>
        </div>
        
        <div>
          <h4 className="text-xs font-bold text-text-primary mb-2 flex items-center gap-1">
            <Banknote className="w-3.5 h-3.5 text-success" /> Eligible Loan Products
          </h4>
          <ul className="space-y-2 text-[11px] text-text-secondary">
            <li className="flex justify-between border-b border-border pb-1">
              <span>Working Capital Loan</span>
              <span className="font-semibold text-text-primary">₹2.5 Cr</span>
            </li>
            <li className="flex justify-between border-b border-border pb-1">
              <span>Business Expansion</span>
              <span className="font-semibold text-text-primary">₹5.0 Cr</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
);

const ReportFooter = () => (
  <div className="mt-12 pt-6 border-t border-border flex justify-between items-end">
    <div className="flex gap-6">
      <div className="flex flex-col items-center">
        <QrCode className="w-16 h-16 text-text-primary mb-2" />
        <span className="text-[9px] text-text-secondary">Scan to Verify</span>
      </div>
      <div className="flex flex-col justify-end">
        <p className="text-[10px] text-text-secondary max-w-xs leading-tight">
          This is an AI-generated report based on connected alternate data sources. 
          Final credit decisions are subject to IDBI Bank's internal credit policy and manual underwriting verification.
        </p>
      </div>
    </div>
    <div className="text-right">
      <div className="w-32 h-12 mb-2 border-b border-text-secondary flex items-end justify-center pb-1">
        <span className="font-signature text-primary italic text-lg opacity-80">System Auth</span>
      </div>
      <p className="text-xs font-semibold text-text-primary flex items-center justify-end gap-1">
        <ShieldCheck className="w-3 h-3 text-success" /> Digital Signature
      </p>
      <p className="text-[10px] text-text-secondary">CreditPulse AI Engine</p>
    </div>
  </div>
);

export default function ReportView() {
  return (
    <div className="min-h-screen bg-background-muted font-sans selection:bg-primary selection:text-white pb-12 w-full">
      {/* Top Action Bar */}
      <div className="bg-white border-b border-border sticky top-0 z-50 mb-8 shadow-sm">
        <div className="max-w-[1000px] mx-auto px-6 h-16 flex items-center justify-between">
          <Link to="/customer/dashboard" className="text-text-secondary hover:text-text-primary flex items-center gap-2 text-sm font-medium transition-colors">
            <ArrowLeft className="w-4 h-4" /> Back to Dashboard
          </Link>
          <div className="flex items-center gap-3">
            <button className="flex items-center gap-2 px-4 py-2 border border-border bg-white hover:bg-background-muted rounded text-sm font-medium text-text-primary transition-colors">
              <Share2 className="w-4 h-4" /> Share
            </button>
            <button className="flex items-center gap-2 px-4 py-2 border border-border bg-white hover:bg-background-muted rounded text-sm font-medium text-text-primary transition-colors">
              <Printer className="w-4 h-4" /> Print
            </button>
            <button className="flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary-hover text-white rounded text-sm font-medium transition-colors">
              <Download className="w-4 h-4" /> Download PDF
            </button>
          </div>
        </div>
      </div>

      {/* A4 Report Container */}
      <main className="max-w-[800px] mx-auto bg-white shadow-lg border border-border">
        {/* Printable Area Padding */}
        <div className="p-12 md:p-16">
          <ReportHeader />
          <BusinessInfo />
          <DataSourcesSection />
          <ScoresSection />
          <AIAnalysisSection />
          <ReportFooter />
        </div>
      </main>
    </div>
  );
}
