import React, { useState } from 'react';
import { 
  Building2, 
  Briefcase, 
  Truck, 
  Settings, 
  ArrowRight,
  BrainCircuit,
  TrendingUp,
  Activity,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';
import { Link } from 'react-router-dom';

const loanProducts = [
  {
    id: 'wc',
    title: 'Working Capital Loan',
    icon: <Building2 className="w-6 h-6" />,
    maxAmount: '₹2.5 Cr',
    estEmi: '₹5.2L',
    rate: '10.5%',
    probability: 92,
    status: 'Pre-approved'
  },
  {
    id: 'exp',
    title: 'Business Expansion',
    icon: <Briefcase className="w-6 h-6" />,
    maxAmount: '₹5.0 Cr',
    estEmi: '₹8.4L',
    rate: '11.0%',
    probability: 85,
    status: 'Pre-approved'
  },
  {
    id: 'machinery',
    title: 'Machinery Term Loan',
    icon: <Settings className="w-6 h-6" />,
    maxAmount: '₹1.5 Cr',
    estEmi: '₹3.1L',
    rate: '11.5%',
    probability: 76,
    status: 'Needs Review'
  },
  {
    id: 'vehicle',
    title: 'Commercial Vehicle',
    icon: <Truck className="w-6 h-6" />,
    maxAmount: '₹80 L',
    estEmi: '₹1.8L',
    rate: '9.5%',
    probability: 95,
    status: 'Pre-approved'
  }
];

const SummaryCard = ({ title, value, subtext }: any) => (
  <div className="bg-white border border-border rounded-card p-5 shadow-sm">
    <p className="text-xs font-medium text-text-secondary mb-1">{title}</p>
    <h3 className="text-2xl font-bold text-text-primary mb-1">{value}</h3>
    <p className="text-[11px] text-text-secondary">{subtext}</p>
  </div>
);

export default function LoanRecommendations() {
  const [loanAmount, setLoanAmount] = useState(25000000); // 2.5 Cr
  const [tenure, setTenure] = useState(36); // months
  const interestRate = 10.5; // %

  const calculateEMI = (p: number, r: number, n: number) => {
    const monthlyRate = r / 12 / 100;
    const emi = (p * monthlyRate * Math.pow(1 + monthlyRate, n)) / (Math.pow(1 + monthlyRate, n) - 1);
    return Math.round(emi);
  };

  const currentEMI = calculateEMI(loanAmount, interestRate, tenure);

  return (
    <div className="p-6 lg:p-8 w-full max-w-[1440px] mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-text-primary mb-1">AI Loan Offers</h1>
        <p className="text-sm text-text-secondary">Credit facilities mapped to your current financial health and operational metrics.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <SummaryCard title="Total Eligible Amount" value="₹4.5 Cr" subtext="Across all credit facilities" />
        <SummaryCard title="Eligibility Confidence" value="High" subtext="Based on AI health analysis" />
        <SummaryCard title="Business Grade" value="A-" subtext="Institutional rating" />
        <SummaryCard title="Health Score" value="82/100" subtext="Top 15% in Manufacturing" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 mb-8">
        
        <div className="xl:col-span-2">
          <h2 className="text-lg font-semibold text-text-primary mb-4">Recommended Products</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {loanProducts.map((product) => (
              <div key={product.id} className="bg-white border border-border rounded-card p-5 shadow-card flex flex-col h-full hover:border-primary/40 transition-colors">
                <div className="flex justify-between items-start mb-4">
                  <div className="p-3 bg-background-muted text-primary rounded">
                    {product.icon}
                  </div>
                  {product.status === 'Pre-approved' ? (
                    <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-success/10 text-success border border-success/20">
                      {product.status}
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-warning/10 text-warning border border-warning/20">
                      {product.status}
                    </span>
                  )}
                </div>
                
                <h3 className="text-base font-semibold text-text-primary mb-4">{product.title}</h3>
                
                <div className="grid grid-cols-2 gap-y-4 mb-6 text-sm flex-grow">
                  <div>
                    <p className="text-xs text-text-secondary mb-0.5">Max Amount</p>
                    <p className="font-semibold text-text-primary">{product.maxAmount}</p>
                  </div>
                  <div>
                    <p className="text-xs text-text-secondary mb-0.5">Interest Rate</p>
                    <p className="font-semibold text-text-primary">{product.rate} p.a.</p>
                  </div>
                  <div>
                    <p className="text-xs text-text-secondary mb-0.5">Est. EMI</p>
                    <p className="font-semibold text-text-primary">{product.estEmi} /mo</p>
                  </div>
                  <div>
                    <p className="text-xs text-text-secondary mb-0.5">Est. Eligibility</p>
                    <p className="font-semibold text-success">{product.probability}%</p>
                  </div>
                </div>

                <Link to="/customer/applications/new" className="w-full py-2.5 bg-primary hover:bg-primary-hover text-white text-sm font-medium rounded transition-colors flex items-center justify-center gap-2">
                  Apply Now <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            ))}
          </div>
        </div>

        <div className="xl:col-span-1 space-y-8">
          <div className="bg-white border border-border rounded-card shadow-card p-6">
            <h2 className="text-base font-semibold text-text-primary mb-6">EMI Calculator</h2>
            
            <div className="mb-6">
              <div className="flex justify-between items-end mb-2">
                <label className="text-sm font-medium text-text-primary">Loan Amount</label>
                <span className="text-lg font-bold text-primary">₹{(loanAmount / 100000).toFixed(1)} Lakhs</span>
              </div>
              <input 
                type="range" 
                min="1000000" 
                max="50000000" 
                step="500000"
                value={loanAmount}
                onChange={(e) => setLoanAmount(Number(e.target.value))}
                className="w-full h-2 bg-background-muted rounded-lg appearance-none cursor-pointer accent-primary"
              />
              <div className="flex justify-between text-xs text-text-secondary mt-2">
                <span>₹10L</span>
                <span>₹5Cr</span>
              </div>
            </div>

            <div className="mb-8">
              <div className="flex justify-between items-end mb-2">
                <label className="text-sm font-medium text-text-primary">Tenure</label>
                <span className="text-lg font-bold text-primary">{tenure} Months</span>
              </div>
              <input 
                type="range" 
                min="12" 
                max="60" 
                step="6"
                value={tenure}
                onChange={(e) => setTenure(Number(e.target.value))}
                className="w-full h-2 bg-background-muted rounded-lg appearance-none cursor-pointer accent-primary"
              />
              <div className="flex justify-between text-xs text-text-secondary mt-2">
                <span>12m</span>
                <span>60m</span>
              </div>
            </div>

            <div className="p-4 bg-background-muted rounded border border-border flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-text-secondary mb-1">Estimated Monthly EMI</p>
                <p className="text-2xl font-bold text-text-primary">₹{(currentEMI / 100000).toFixed(2)}L</p>
              </div>
              <div className="text-right">
                <p className="text-xs text-text-secondary mb-1">Interest</p>
                <p className="text-sm font-semibold text-primary">{interestRate}% p.a.</p>
              </div>
            </div>
          </div>

          <div className="bg-primary/5 border border-primary/20 rounded-card p-6">
            <div className="flex items-center gap-2 mb-4 pb-4 border-b border-primary/10">
              <BrainCircuit className="w-5 h-5 text-primary" />
              <h3 className="text-base font-semibold text-text-primary">AI Recommendation Logic</h3>
            </div>
            
            <div className="space-y-6">
              <div>
                <h4 className="text-sm font-semibold text-text-primary mb-1">Working Capital Loan</h4>
                <p className="text-xs text-text-secondary leading-relaxed mb-2">
                  <strong>Why recommended:</strong> Helps bridge the 65-day gap between providing services and receiving payments from your customers.
                </p>
                <p className="text-xs text-text-secondary leading-relaxed mb-2">
                  <strong>Key Indicators:</strong> Consistent sales volume vs delayed cash realization.
                </p>
                <p className="text-xs text-text-secondary leading-relaxed mb-2">
                  <strong>Data Sources:</strong> GSTR-1, Bank Statements, Invoices.
                </p>
                <p className="text-xs text-text-primary font-medium leading-relaxed">
                  <strong>How to increase limit:</strong> Reducing average collection time below 45 days could unlock up to ₹3.5 Cr.
                </p>
              </div>
              
              <div className="border-t border-primary/10 pt-4">
                <h4 className="text-sm font-semibold text-text-primary mb-1">Machinery Term Loan</h4>
                <p className="text-xs text-text-secondary leading-relaxed mb-2">
                  <strong>Why recommended:</strong> Supports business expansion for your manufacturing unit.
                </p>
                <p className="text-xs text-text-secondary leading-relaxed">
                  <strong>Data Sources:</strong> Utility Bills (Electricity consumption), Bank Statements.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white border border-border rounded-card shadow-card p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-base font-semibold text-text-primary mb-1">Business Improvement Simulator</h2>
            <p className="text-sm text-text-secondary">Simulate actions to improve your Health Score and Loan Eligibility.</p>
          </div>
          <Activity className="w-5 h-5 text-text-secondary hidden sm:block" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-1 border-r border-border pr-6">
            <h4 className="text-sm font-semibold text-text-primary mb-4">Current State</h4>
            <div className="space-y-4">
              <div className="flex justify-between items-center pb-2 border-b border-border">
                <span className="text-sm text-text-secondary">Health Score</span>
                <span className="text-sm font-bold text-text-primary">82</span>
              </div>
              <div className="flex justify-between items-center pb-2 border-b border-border">
                <span className="text-sm text-text-secondary">WC Eligibility</span>
                <span className="text-sm font-bold text-text-primary">₹2.5 Cr</span>
              </div>
              <div className="flex justify-between items-center pb-2 border-b border-border">
                <span className="text-sm text-text-secondary">Interest Rate</span>
                <span className="text-sm font-bold text-text-primary">10.5%</span>
              </div>
            </div>
          </div>

          <div className="md:col-span-1 border-r border-border pr-6">
            <h4 className="text-sm font-semibold text-text-primary mb-4">AI Recommended Actions</h4>
            <div className="space-y-3">
              <label className="flex items-start gap-3 cursor-pointer group">
                <input type="checkbox" className="mt-1 border-border rounded text-primary focus:ring-primary w-4 h-4 cursor-pointer" defaultChecked />
                <div>
                  <span className="text-sm font-medium text-text-primary group-hover:text-primary transition-colors block">Reduce collection cycle to 45 days</span>
                  <span className="text-xs text-text-secondary">+4 Score Impact</span>
                </div>
              </label>
              <label className="flex items-start gap-3 cursor-pointer group">
                <input type="checkbox" className="mt-1 border-border rounded text-primary focus:ring-primary w-4 h-4 cursor-pointer" />
                <div>
                  <span className="text-sm font-medium text-text-primary group-hover:text-primary transition-colors block">Diversify Top 3 Clients</span>
                  <span className="text-xs text-text-secondary">+6 Score Impact</span>
                </div>
              </label>
            </div>
          </div>

          <div className="md:col-span-1">
            <h4 className="text-sm font-semibold text-text-primary mb-4 text-success flex items-center gap-2">
              <TrendingUp className="w-4 h-4" /> Projected State
            </h4>
            <div className="space-y-4">
              <div className="flex justify-between items-center pb-2 border-b border-border">
                <span className="text-sm text-text-secondary">Projected Score</span>
                <span className="text-sm font-bold text-success">86</span>
              </div>
              <div className="flex justify-between items-center pb-2 border-b border-border">
                <span className="text-sm text-text-secondary">WC Eligibility</span>
                <span className="text-sm font-bold text-success">₹3.2 Cr</span>
              </div>
              <div className="flex justify-between items-center pb-2 border-b border-border">
                <span className="text-sm text-text-secondary">Interest Rate</span>
                <span className="text-sm font-bold text-success">10.0%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
