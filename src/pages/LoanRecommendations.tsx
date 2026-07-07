import React, { useState } from 'react';
import {
  Building2,
  Briefcase,
  Truck,
  Settings,
  ArrowRight,
  BrainCircuit,
  TrendingUp,
  Activity
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { useBusinessDetail } from '../lib/api/hooks';
import { DEMO_BUSINESS_ID, gradeFromScore } from '../lib/customer';
import { formatINRCompact, formatPct } from '../lib/format';
import { PageSkeleton } from '../components/Skeleton';

const calculateEMI = (p: number, r: number, n: number) => {
  const monthlyRate = r / 12 / 100;
  const emi = (p * monthlyRate * Math.pow(1 + monthlyRate, n)) / (Math.pow(1 + monthlyRate, n) - 1);
  return Math.round(emi);
};

const SummaryCard = ({ title, value, subtext }: any) => (
  <div className="bg-white border border-border rounded-card p-5 shadow-sm">
    <p className="text-xs font-medium text-text-secondary mb-1">{title}</p>
    <h3 className="text-2xl font-bold text-text-primary mb-1 tnum">{value}</h3>
    <p className="text-[11px] text-text-secondary">{subtext}</p>
  </div>
);

// Score-improvement actions with capped, clearly-labelled simulated impact
const SIM_ACTIONS = [
  { id: 'gst', label: 'Maintain 12/12 on-time GST filings', impact: 3 },
  { id: 'buffer', label: 'Increase cash buffer to 30+ days', impact: 5 },
];

export default function LoanRecommendations() {
  const { data, isLoading, error } = useBusinessDetail(DEMO_BUSINESS_ID);
  const [loanAmount, setLoanAmount] = useState<number | null>(null);
  const [tenure, setTenure] = useState<number | null>(null);
  const [selectedActions, setSelectedActions] = useState<string[]>([]);

  if (isLoading) return <PageSkeleton label="Loading loan offers" />;
  if (error || !data) {
    return (
      <div className="p-6 text-center text-error">
        <p className="font-semibold">Error loading loan offers</p>
        <p className="text-xs mt-1">Make sure the FastAPI server is running on port 8000.</p>
      </div>
    );
  }

  const score = data.score.score;
  const rec = data.recommendation;
  // Base rate = lower bound of the model's interest band (e.g. "10.5% - 12.5%")
  const baseRate = parseFloat(rec.interest_band) || 10.5;

  // Product ladder scaled from the model's recommended exposure
  const loanProducts = [
    { id: 'wc', title: 'IDBI MSME Cash Credit (CC)', icon: <Building2 className="w-6 h-6" aria-hidden="true" />, amount: rec.loan_amount, rate: baseRate, preApproved: score >= 55 },
    { id: 'exp', title: 'IDBI MSME Term Loan', icon: <Briefcase className="w-6 h-6" aria-hidden="true" />, amount: Math.round(rec.loan_amount * 1.5), rate: baseRate + 0.5, preApproved: score >= 75 },
    { id: 'machinery', title: 'IDBI Equipment Finance Scheme', icon: <Settings className="w-6 h-6" aria-hidden="true" />, amount: Math.round(rec.loan_amount * 0.6), rate: baseRate + 1.0, preApproved: score >= 65 },
    { id: 'vehicle', title: 'IDBI Commercial Vehicle Loan', icon: <Truck className="w-6 h-6" aria-hidden="true" />, amount: Math.round(rec.loan_amount * 0.35), rate: baseRate - 1.0, preApproved: score >= 55 },
  ];

  const totalEligible = loanProducts.filter((p) => p.preApproved).reduce((acc, p) => acc + p.amount, 0);

  const sliderMax = Math.max(rec.loan_amount * 2, 1000000);
  const currentAmount = loanAmount ?? rec.loan_amount;
  const currentTenure = tenure ?? rec.tenure_months;
  const currentEMI = calculateEMI(currentAmount, baseRate, currentTenure);

  // Simulator: real arithmetic on the live score
  const simImpact = SIM_ACTIONS.filter((a) => selectedActions.includes(a.id)).reduce((acc, a) => acc + a.impact, 0);
  const projectedScore = Math.min(100, score + simImpact);
  const projectedEligibility = Math.round(rec.loan_amount * (1 + simImpact * 0.05));
  const projectedRate = Math.max(8, baseRate - simImpact * 0.1);

  const toggleAction = (id: string) =>
    setSelectedActions((prev) => prev.includes(id) ? prev.filter((a) => a !== id) : [...prev, id]);

  return (
    <div className="p-6 lg:p-8 w-full max-w-[1440px] mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-text-primary mb-1">AI Loan Offers</h1>
        <p className="text-sm text-text-secondary">Credit facilities mapped to the live financial health assessment of {data.profile.name}.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <SummaryCard title="Total Eligible Amount" value={formatINRCompact(totalEligible)} subtext="Across pre-approved facilities" />
        <SummaryCard title="Model Decision" value={rec.decision} subtext="Live Agent 2 output" />
        <SummaryCard title="Business Grade" value={gradeFromScore(score)} subtext="Derived from health score" />
        <SummaryCard title="Health Score" value={`${score}/100`} subtext={`${data.score.band} risk band`} />
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
                  {product.preApproved ? (
                    <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-success/10 text-success border border-success/20">
                      Pre-approved
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-warning/10 text-warning border border-warning/20">
                      Needs Review
                    </span>
                  )}
                </div>

                <h3 className="text-base font-semibold text-text-primary mb-4">{product.title}</h3>

                <div className="grid grid-cols-2 gap-y-4 mb-6 text-sm flex-grow">
                  <div>
                    <p className="text-xs text-text-secondary mb-0.5">Max Amount</p>
                    <p className="font-semibold text-text-primary tnum">{formatINRCompact(product.amount)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-text-secondary mb-0.5">Interest Rate</p>
                    <p className="font-semibold text-text-primary tnum">{product.rate.toFixed(1)}% p.a.</p>
                  </div>
                  <div>
                    <p className="text-xs text-text-secondary mb-0.5">Est. EMI ({rec.tenure_months}m)</p>
                    <p className="font-semibold text-text-primary tnum">{formatINRCompact(calculateEMI(product.amount, product.rate, rec.tenure_months))} /mo</p>
                  </div>
                  <div>
                    <p className="text-xs text-text-secondary mb-0.5">Tenure</p>
                    <p className="font-semibold text-text-primary tnum">{rec.tenure_months} months</p>
                  </div>
                </div>

                <Link to="/customer/applications" className="w-full py-2.5 bg-primary hover:bg-primary-hover text-white text-sm font-medium rounded transition-colors flex items-center justify-center gap-2">
                  View Application <ArrowRight className="w-4 h-4" aria-hidden="true" />
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
                <label htmlFor="emi-amount" className="text-sm font-medium text-text-primary">Loan Amount</label>
                <span className="text-lg font-bold text-primary tnum">{formatINRCompact(currentAmount)}</span>
              </div>
              <input
                id="emi-amount"
                type="range"
                min={500000}
                max={sliderMax}
                step={100000}
                value={currentAmount}
                onChange={(e) => setLoanAmount(Number(e.target.value))}
                className="w-full h-2 bg-background-muted rounded-lg appearance-none cursor-pointer accent-primary"
              />
              <div className="flex justify-between text-xs text-text-secondary mt-2">
                <span className="tnum">{formatINRCompact(500000)}</span>
                <span className="tnum">{formatINRCompact(sliderMax)}</span>
              </div>
            </div>

            <div className="mb-8">
              <div className="flex justify-between items-end mb-2">
                <label htmlFor="emi-tenure" className="text-sm font-medium text-text-primary">Tenure</label>
                <span className="text-lg font-bold text-primary tnum">{currentTenure} Months</span>
              </div>
              <input
                id="emi-tenure"
                type="range"
                min={12}
                max={60}
                step={6}
                value={currentTenure}
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
                <p className="text-2xl font-bold text-text-primary tnum">{formatINRCompact(currentEMI)}</p>
              </div>
              <div className="text-right">
                <p className="text-xs text-text-secondary mb-1">Interest</p>
                <p className="text-sm font-semibold text-primary tnum">{baseRate.toFixed(1)}% p.a.</p>
              </div>
            </div>
          </div>

          <div className="bg-primary/5 border border-primary/20 rounded-card p-6">
            <div className="flex items-center gap-2 mb-4 pb-4 border-b border-primary/10">
              <BrainCircuit className="w-5 h-5 text-primary" aria-hidden="true" />
              <h3 className="text-base font-semibold text-text-primary">AI Recommendation Logic</h3>
            </div>

            <div className="space-y-4">
              <p className="text-xs text-text-secondary leading-relaxed">
                <strong className="text-text-primary">Why these limits:</strong> The Agent 2 model recommends a base exposure
                of {formatINRCompact(rec.loan_amount)} — roughly 3× your average monthly revenue — over {rec.tenure_months} months
                at {rec.interest_band}, based on your {score}/100 health score.
              </p>
              <p className="text-xs text-text-secondary leading-relaxed">
                <strong className="text-text-primary">Top score driver:</strong> {data.factors[0].label} ({formatPct(data.factors[0].weight)} weight). {data.factors[0].detail}
              </p>
              <p className="text-xs text-text-secondary leading-relaxed">
                <strong className="text-text-primary">Data sources:</strong> Bank statements (12 months), GST filing timeline, engineered cash-flow metrics.
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white border border-border rounded-card shadow-card p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-base font-semibold text-text-primary mb-1">Business Improvement Simulator</h2>
            <p className="text-sm text-text-secondary">Simulate actions to project your health score and eligibility. Projections are illustrative.</p>
          </div>
          <Activity className="w-5 h-5 text-text-secondary hidden sm:block" aria-hidden="true" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-1 md:border-r border-border md:pr-6">
            <h4 className="text-sm font-semibold text-text-primary mb-4">Current State</h4>
            <div className="space-y-4">
              <div className="flex justify-between items-center pb-2 border-b border-border">
                <span className="text-sm text-text-secondary">Health Score</span>
                <span className="text-sm font-bold text-text-primary tnum">{score}</span>
              </div>
              <div className="flex justify-between items-center pb-2 border-b border-border">
                <span className="text-sm text-text-secondary">WC Eligibility</span>
                <span className="text-sm font-bold text-text-primary tnum">{formatINRCompact(rec.loan_amount)}</span>
              </div>
              <div className="flex justify-between items-center pb-2 border-b border-border">
                <span className="text-sm text-text-secondary">Interest Rate</span>
                <span className="text-sm font-bold text-text-primary tnum">{baseRate.toFixed(1)}%</span>
              </div>
            </div>
          </div>

          <div className="md:col-span-1 md:border-r border-border md:pr-6">
            <h4 className="text-sm font-semibold text-text-primary mb-4">AI Recommended Actions</h4>
            <div className="space-y-3">
              {SIM_ACTIONS.map((action) => (
                <label key={action.id} className="flex items-start gap-3 cursor-pointer group">
                  <input
                    type="checkbox"
                    checked={selectedActions.includes(action.id)}
                    onChange={() => toggleAction(action.id)}
                    className="mt-1 border-border rounded text-primary focus:ring-primary w-4 h-4 cursor-pointer"
                  />
                  <div>
                    <span className="text-sm font-medium text-text-primary group-hover:text-primary transition-colors block">{action.label}</span>
                    <span className="text-xs text-text-secondary tnum">+{action.impact} Score Impact</span>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div className="md:col-span-1">
            <h4 className="text-sm font-semibold text-text-primary mb-4 text-success flex items-center gap-2">
              <TrendingUp className="w-4 h-4" aria-hidden="true" /> Projected State
            </h4>
            <div className="space-y-4">
              <div className="flex justify-between items-center pb-2 border-b border-border">
                <span className="text-sm text-text-secondary">Projected Score</span>
                <span className="text-sm font-bold text-success tnum">{projectedScore}</span>
              </div>
              <div className="flex justify-between items-center pb-2 border-b border-border">
                <span className="text-sm text-text-secondary">WC Eligibility</span>
                <span className="text-sm font-bold text-success tnum">{formatINRCompact(projectedEligibility)}</span>
              </div>
              <div className="flex justify-between items-center pb-2 border-b border-border">
                <span className="text-sm text-text-secondary">Interest Rate</span>
                <span className="text-sm font-bold text-success tnum">{projectedRate.toFixed(1)}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
