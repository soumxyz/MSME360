import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeft,
  FileText,
  Smartphone,
  Landmark,
  Briefcase,
  ScrollText,
  FileStack,
  CheckCircle2,
  Clock,
  Download,
  Phone,
  XCircle,
  Building2
} from 'lucide-react';

const steps = [
  { title: 'Application Submitted', date: '05 Jul, 10:00 AM', status: 'completed' },
  { title: 'Financial Assessment Complete', date: '05 Jul, 10:05 AM', status: 'completed' },
  { title: 'Alternate Data Verified', date: '06 Jul, 02:30 PM', status: 'completed' },
  { title: 'Assigned to Loan Officer', date: '07 Jul, 09:15 AM', status: 'completed' },
  { title: 'Manual Review', date: 'In Progress', status: 'current' },
  { title: 'Decision', date: 'Expected 08 Jul', status: 'pending' },
];

export default function ApplicationDetails() {
  const { id } = useParams();
  
  return (
    <div className="p-6 lg:p-8 w-full max-w-[1000px] mx-auto">
      <div className="mb-6">
        <Link to="/customer/applications" className="inline-flex items-center gap-2 text-sm font-medium text-text-secondary hover:text-primary transition-colors mb-4">
          <ArrowLeft className="w-4 h-4" /> Back to Applications
        </Link>
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold text-text-primary mb-1">Application {id || 'APP-10294'}</h1>
            <p className="text-sm text-text-secondary">Track the progress of your loan request.</p>
          </div>
          <div className="flex items-center gap-3">
            <button className="px-4 py-2 bg-white border border-border hover:bg-background-muted text-text-primary text-sm font-medium rounded transition-colors flex items-center gap-2">
              <Phone className="w-4 h-4" /> Contact RM
            </button>
            <button className="px-4 py-2 bg-white border border-border hover:bg-background-muted text-text-primary text-sm font-medium rounded transition-colors flex items-center gap-2">
              <Download className="w-4 h-4" /> Download
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white border border-border rounded-card p-5 shadow-sm">
          <p className="text-xs font-medium text-text-secondary mb-1">Loan Type</p>
          <h3 className="text-base font-semibold text-text-primary">Working Capital Loan</h3>
        </div>
        <div className="bg-white border border-border rounded-card p-5 shadow-sm">
          <p className="text-xs font-medium text-text-secondary mb-1">Applied Amount</p>
          <h3 className="text-base font-semibold text-text-primary">₹2.5 Cr</h3>
        </div>
        <div className="bg-white border border-border rounded-card p-5 shadow-sm">
          <p className="text-xs font-medium text-text-secondary mb-1">Current Status</p>
          <div className="flex items-center gap-2 mt-0.5">
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-primary/10 text-primary border border-primary/20">Under Review</span>
            <span className="text-xs text-text-secondary">Expected 08 Jul</span>
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
                    <div className={`absolute left-[11px] top-6 bottom-[-24px] w-0.5 ${step.status === 'completed' ? 'bg-success' : 'bg-border'}`}></div>
                  )}
                  <div className="relative z-10 flex-shrink-0 mt-0.5">
                    {step.status === 'completed' && <CheckCircle2 className="w-6 h-6 text-success bg-white" />}
                    {step.status === 'current' && <Clock className="w-6 h-6 text-primary bg-white" />}
                    {step.status === 'pending' && <div className="w-6 h-6 rounded-full border-2 border-border bg-white" />}
                  </div>
                  <div>
                    <h4 className={`text-sm font-semibold mb-0.5 ${step.status === 'pending' ? 'text-text-secondary' : 'text-text-primary'}`}>
                      {step.title}
                    </h4>
                    <p className="text-xs text-text-secondary">{step.date}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Sidebar Info */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white border border-border rounded-card p-6 shadow-card">
            <h3 className="text-sm font-semibold text-text-primary mb-4 border-b border-border pb-2">Assigned Branch</h3>
            <div className="flex items-start gap-3">
              <Building2 className="w-5 h-5 text-primary mt-0.5" />
              <div>
                <p className="text-sm font-medium text-text-primary mb-1">Mumbai Main Branch</p>
                <p className="text-xs text-text-secondary leading-relaxed">Nariman Point, Mumbai, Maharashtra 400021</p>
              </div>
            </div>
          </div>

          <div className="bg-white border border-border rounded-card p-6 shadow-card">
            <h3 className="text-sm font-semibold text-text-primary mb-4 border-b border-border pb-2">Connected Documents</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-text-secondary">
                  <FileText className="w-4 h-4" /> GST Returns
                </div>
                <CheckCircle2 className="w-4 h-4 text-success" />
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-text-secondary">
                  <Smartphone className="w-4 h-4" /> UPI Data
                </div>
                <CheckCircle2 className="w-4 h-4 text-success" />
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-text-secondary">
                  <Landmark className="w-4 h-4" /> Account Aggregator
                </div>
                <CheckCircle2 className="w-4 h-4 text-success" />
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-text-secondary">
                  <Briefcase className="w-4 h-4" /> EPFO
                </div>
                <CheckCircle2 className="w-4 h-4 text-success" />
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-text-secondary">
                  <ScrollText className="w-4 h-4" /> Bank Statements
                </div>
                <CheckCircle2 className="w-4 h-4 text-success" />
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-text-secondary">
                  <FileStack className="w-4 h-4" /> Sales Invoices
                </div>
                <CheckCircle2 className="w-4 h-4 text-success" />
              </div>
            </div>
          </div>

          <button className="w-full py-2 bg-white border border-border hover:bg-error/5 hover:border-error/20 text-error text-sm font-medium rounded transition-colors flex items-center justify-center gap-2">
            <XCircle className="w-4 h-4" /> Withdraw Application
          </button>
        </div>

      </div>
    </div>
  );
}
