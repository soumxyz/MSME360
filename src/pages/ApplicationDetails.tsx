import React from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft,
  FileText,
  ScrollText,
  CheckCircle2,
  Clock,
  XCircle,
  Building2,
  BrainCircuit,
  Activity
} from 'lucide-react';
import { useBusinessDetail } from '../lib/api/hooks';
import { DEMO_BUSINESS_ID } from '../lib/customer';
import { formatINRCompact, formatDate } from '../lib/format';
import { PageSkeleton } from '../components/Skeleton';

export default function ApplicationDetails() {
  const { id } = useParams();
  const businessId = id ?? DEMO_BUSINESS_ID;
  const { data, isLoading, error } = useBusinessDetail(businessId);

  if (isLoading) return <PageSkeleton label="Loading application details" />;
  if (error || !data) {
    return (
      <div className="p-6 text-center text-error">
        <p className="font-semibold">Error loading application</p>
        <p className="text-xs mt-1">Make sure the FastAPI server is running on port 8000.</p>
        <Link to="/customer/applications" className="inline-flex items-center gap-2 mt-4 text-sm font-medium text-primary hover:underline">
          <ArrowLeft className="w-4 h-4" aria-hidden="true" /> Back to Applications
        </Link>
      </div>
    );
  }

  const status = data.officer_status;
  const isDecided = status !== 'Pending' && status !== 'Info Requested';

  // Timeline stages driven by the real officer decision status
  const steps = [
    { title: 'Application Submitted', detail: formatDate(data.applied_at), state: 'completed' },
    { title: 'Compliance Checks Passed (Agent 1)', detail: 'Bank statement + GST verified', state: 'completed' },
    { title: `AI Health Score Computed: ${data.score.score}/100 (Agent 2)`, detail: `${data.score.band} risk band`, state: 'completed' },
    { title: 'Officer Review', detail: isDecided ? 'Review complete' : 'In progress', state: isDecided ? 'completed' : 'current' },
    { title: `Decision: ${isDecided ? status : 'Pending'}`, detail: isDecided ? 'Recorded in audit trail' : 'Awaiting officer decision', state: isDecided ? (status === 'Rejected' ? 'rejected' : 'completed') : 'pending' },
  ];

  return (
    <div className="p-6 lg:p-8 w-full max-w-[1000px] mx-auto">
      <div className="mb-6">
        <Link to="/customer/applications" className="inline-flex items-center gap-2 text-sm font-medium text-text-secondary hover:text-primary transition-colors mb-4">
          <ArrowLeft className="w-4 h-4" aria-hidden="true" /> Back to Applications
        </Link>
        <div>
          <h1 className="text-2xl font-semibold text-text-primary mb-1">Application {data.business_id}</h1>
          <p className="text-sm text-text-secondary">Working capital application for {data.profile.name}.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white border border-border rounded-card p-5 shadow-sm">
          <p className="text-xs font-medium text-text-secondary mb-1">Loan Type</p>
          <h3 className="text-base font-semibold text-text-primary">Working Capital Loan</h3>
        </div>
        <div className="bg-white border border-border rounded-card p-5 shadow-sm">
          <p className="text-xs font-medium text-text-secondary mb-1">Recommended Amount</p>
          <h3 className="text-base font-semibold text-text-primary tnum">{formatINRCompact(data.recommendation.loan_amount)}</h3>
        </div>
        <div className="bg-white border border-border rounded-card p-5 shadow-sm">
          <p className="text-xs font-medium text-text-secondary mb-1">Current Status</p>
          <div className="flex items-center gap-2 mt-0.5">
            {status === 'Approved' || status === 'Conditional' ? (
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-success/10 text-success border border-success/20">{status}</span>
            ) : status === 'Rejected' ? (
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-error/10 text-error border border-error/20">Rejected</span>
            ) : (
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-primary/10 text-primary border border-primary/20">Under Review</span>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

        {/* Timeline */}
        <div className="lg:col-span-2 bg-white border border-border rounded-card p-6 shadow-card">
          <h3 className="text-base font-semibold text-text-primary mb-6">Application Timeline</h3>
          <div className="space-y-6">
            {steps.map((step, index) => {
              const isLast = index === steps.length - 1;
              return (
                <div key={index} className="flex gap-4 relative">
                  {!isLast && (
                    <div className={`absolute left-[11px] top-6 bottom-[-24px] w-0.5 ${step.state === 'completed' ? 'bg-success' : 'bg-border'}`}></div>
                  )}
                  <div className="relative z-10 flex-shrink-0 mt-0.5">
                    {step.state === 'completed' && <CheckCircle2 className="w-6 h-6 text-success bg-white" aria-hidden="true" />}
                    {step.state === 'rejected' && <XCircle className="w-6 h-6 text-error bg-white" aria-hidden="true" />}
                    {step.state === 'current' && <Clock className="w-6 h-6 text-primary bg-white" aria-hidden="true" />}
                    {step.state === 'pending' && <div className="w-6 h-6 rounded-full border-2 border-border bg-white" />}
                  </div>
                  <div>
                    <h4 className={`text-sm font-semibold mb-0.5 ${step.state === 'pending' ? 'text-text-secondary' : 'text-text-primary'}`}>
                      {step.title}
                    </h4>
                    <p className="text-xs text-text-secondary">{step.detail}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Sidebar Info */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white border border-border rounded-card p-6 shadow-card">
            <h3 className="text-sm font-semibold text-text-primary mb-4 border-b border-border pb-2">Business Profile</h3>
            <div className="flex items-start gap-3">
              <Building2 className="w-5 h-5 text-primary mt-0.5" aria-hidden="true" />
              <div>
                <p className="text-sm font-medium text-text-primary mb-1">{data.profile.name}</p>
                <p className="text-xs text-text-secondary leading-relaxed">
                  {data.profile.industry} • {data.profile.city}, {data.profile.state}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white border border-border rounded-card p-6 shadow-card">
            <h3 className="text-sm font-semibold text-text-primary mb-4 border-b border-border pb-2">Assessment Inputs</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-text-secondary">
                  <ScrollText className="w-4 h-4" aria-hidden="true" /> Bank Statements (12 mo)
                </div>
                <CheckCircle2 className="w-4 h-4 text-success" aria-hidden="true" />
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-text-secondary">
                  <FileText className="w-4 h-4" aria-hidden="true" /> GST Filing Timeline
                </div>
                <CheckCircle2 className="w-4 h-4 text-success" aria-hidden="true" />
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-text-secondary">
                  <Activity className="w-4 h-4" aria-hidden="true" /> Cash Flow Metrics
                </div>
                <CheckCircle2 className="w-4 h-4" aria-hidden="true" />
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-text-secondary">
                  <BrainCircuit className="w-4 h-4" aria-hidden="true" /> SHAP Attribution
                </div>
                <CheckCircle2 className="w-4 h-4 text-success" aria-hidden="true" />
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
