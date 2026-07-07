import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { 
  Activity, 
  FileText, 
  Smartphone, 
  Landmark, 
  Briefcase, 
  Receipt, 
  ScrollText, 
  Lightbulb, 
  FileStack,
  CheckCircle2,
  AlertCircle,
  XCircle,
  Loader2,
  ArrowRight,
  ShieldCheck,
  Upload,
  X
} from 'lucide-react';
import { submitIntake } from '../lib/api';
import { addAuditEvent } from '../lib/audit';

type ConnectionStatus = 'disconnected' | 'connecting' | 'connected';
type VerdictType = "GREEN" | "YELLOW" | "RED" | null;

interface DataSource {
  id: string;
  name: string;
  icon: React.ReactNode;
  description: string;
}

const DATA_SOURCES: DataSource[] = [
  { id: 'gst', name: 'GST Returns', description: 'GSTR-1 & GSTR-3B data via GSTN', icon: <FileText className="w-6 h-6" /> },
  { id: 'upi', name: 'UPI Transactions', description: 'Merchant QR collections & VPA', icon: <Smartphone className="w-6 h-6" /> },
  { id: 'aa', name: 'Account Aggregator', description: 'Secure consent-based bank data', icon: <Landmark className="w-6 h-6" /> },
  { id: 'epfo', name: 'EPFO', description: 'Employee provident fund records', icon: <Briefcase className="w-6 h-6" /> },
  { id: 'bank', name: 'Bank Statements', description: 'Upload CSV statements securely', icon: <ScrollText className="w-6 h-6" /> },
  { id: 'itr', name: 'Income Tax Returns', description: 'ITR-3 / ITR-4 acknowledgments', icon: <Receipt className="w-6 h-6" /> },
  { id: 'utility', name: 'Utility Bills', description: 'Electricity & broadband payment history', icon: <Lightbulb className="w-6 h-6" /> },
  { id: 'invoices', name: 'Sales Invoices', description: 'ERP or accounting software sync', icon: <FileStack className="w-6 h-6" /> },
];

const generateBankCSV = (months: number, creditsPerMonth: number, reconciled: boolean): string => {
  let csv = "Date,Credit,Debit,Running_Balance\n";
  let balance = 10000;
  const startYear = 2025;
  for (let m = 0; m < months; m++) {
    const year = startYear + Math.floor(m / 12);
    const monthStr = String((m % 12) + 1).padStart(2, '0');
    for (let c = 0; c < creditsPerMonth; c++) {
      const dayStr = String((c % 28) + 1).padStart(2, '0');
      const cr = 2000 + (c * 100);
      const db = 1500;
      balance = balance + cr - db;
      const actualBalance = (!reconciled && m === 1 && c === 5) ? balance - 5000 : balance;
      csv += `${year}-${monthStr}-${dayStr},${cr},${db},${actualBalance}\n`;
    }
  }
  return csv;
};

const IntegrationCard = ({ 
  source, 
  status, 
  onConnect 
}: { 
  source: DataSource, 
  status: ConnectionStatus, 
  onConnect: () => void 
}) => {
  return (
    <div className="bg-white border border-border rounded-card shadow-card p-5 flex flex-col h-full transition-all hover:border-primary/30 hover:shadow-md">
      <div className="flex items-start justify-between mb-4">
        <div className={`w-12 h-12 rounded flex items-center justify-center ${status === 'connected' ? 'bg-success/10 text-success' : 'bg-background-muted text-primary'}`}>
          {source.icon}
        </div>
        <div>
          {status === 'connected' && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-success/10 text-success text-xs font-medium border border-success/20">
              <CheckCircle2 className="w-3.5 h-3.5" /> Connected
            </span>
          )}
          {status === 'connecting' && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-warning/10 text-warning text-xs font-medium border border-warning/20">
              <Loader2 className="w-3.5 h-3.5 animate-spin" /> Connecting
            </span>
          )}
          {status === 'disconnected' && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-background-muted text-text-secondary text-xs font-medium border border-border">
              <AlertCircle className="w-3.5 h-3.5" /> Not Connected
            </span>
          )}
        </div>
      </div>
      
      <div className="flex-grow">
        <h3 className="text-base font-semibold text-text-primary mb-1">{source.name}</h3>
        <p className="text-xs text-text-secondary leading-relaxed">{source.description}</p>
      </div>

      <div className="mt-6 pt-4 border-t border-border">
        {status === 'connected' ? (
          <button 
            className="w-full py-2 bg-white border border-border rounded text-sm font-medium text-text-primary hover:bg-background-muted transition-colors cursor-pointer"
            onClick={onConnect}
          >
            Disconnect
          </button>
        ) : (
          <button 
            disabled={status === 'connecting'}
            className="w-full py-2 bg-primary hover:bg-primary-hover text-white rounded text-sm font-medium transition-colors disabled:opacity-70 disabled:cursor-not-allowed cursor-pointer"
            onClick={onConnect}
          >
            {status === 'connecting' ? 'Authenticating...' : 'Connect'}
          </button>
        )}
      </div>
    </div>
  );
};

const AnalysisWorkflow = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const navigate = useNavigate();

  const steps = [
    { title: "Aggregating Data Sources", desc: "Securely fetching data from connected integrations." },
    { title: "Normalizing Financial Records", desc: "Structuring unstructured data formats." },
    { title: "AI Pattern Recognition", desc: "Analyzing cash flow, working capital, and repayment capacity." },
    { title: "Generating Health Score", desc: "Calculating institutional-grade credit score." },
    { title: "Formulating Recommendations", desc: "Mapping profile to IDBI Bank credit facilities." }
  ];

  useEffect(() => {
    if (currentStep < steps.length) {
      const timer = setTimeout(() => {
        setCurrentStep(prev => prev + 1);
      }, 1500);
      return () => clearTimeout(timer);
    } else {
      const timer = setTimeout(() => {
        navigate('/customer/dashboard');
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [currentStep, steps.length, navigate]);

  return (
    <div className="w-full max-w-2xl mx-auto py-12 px-4">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white border border-border rounded-card shadow-card p-8 md:p-12"
      >
        <div className="text-center mb-10">
          <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
            <Activity className="w-8 h-8 text-primary animate-pulse" />
          </div>
          <h2 className="text-2xl font-semibold text-text-primary mb-2">Analyzing Financial Health</h2>
          <p className="text-sm text-text-secondary">Please wait while our AI processes your connected data sources.</p>
        </div>

        <div className="space-y-6">
          {steps.map((step, index) => {
            const isActive = index === currentStep;
            const isCompleted = index < currentStep;
            const isPending = index > currentStep;

            return (
              <div key={index} className="flex items-start gap-4">
                <div className="mt-0.5">
                  {isCompleted && <CheckCircle2 className="w-5 h-5 text-success" />}
                  {isActive && <Loader2 className="w-5 h-5 text-primary animate-spin" />}
                  {isPending && <div className="w-5 h-5 rounded-full border-2 border-border" />}
                </div>
                <div>
                  <h4 className={`text-sm font-semibold mb-0.5 ${isActive || isCompleted ? 'text-text-primary' : 'text-text-secondary'}`}>
                    {step.title}
                  </h4>
                  <p className="text-xs text-text-secondary">{step.desc}</p>
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-10 pt-8 border-t border-border">
          <div className="flex items-center justify-between text-xs font-medium text-text-secondary mb-2">
            <span>Overall Progress</span>
            <span>{Math.round((currentStep / steps.length) * 100)}%</span>
          </div>
          <div className="w-full h-2 bg-background-muted rounded-full overflow-hidden">
            <motion.div 
              className="h-full bg-primary"
              initial={{ width: 0 }}
              animate={{ width: `${(currentStep / steps.length) * 100}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>

      </motion.div>
    </div>
  );
};

export default function BusinessRegistration() {
  const [statuses, setStatuses] = useState<Record<string, ConnectionStatus>>(
    DATA_SOURCES.reduce((acc, source) => ({ ...acc, [source.id]: 'disconnected' }), {})
  );
  
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isUploaderOpen, setIsUploaderOpen] = useState(false);

  // Uploader compliance states
  const [isParsing, setIsParsing] = useState(false);
  const [verdict, setVerdict] = useState<VerdictType>(null);
  const [checks, setChecks] = useState<any[]>([]);
  const [uploadedFileName, setUploadedFileName] = useState<string>('');
  const [uploadError, setUploadError] = useState<string | null>(null);

  const handleConnect = (id: string) => {
    if (statuses[id] === 'connected') {
      setStatuses(prev => ({ ...prev, [id]: 'disconnected' }));
      return;
    }
    
    if (id === 'bank') {
      setIsUploaderOpen(true);
      return;
    }

    setStatuses(prev => ({ ...prev, [id]: 'connecting' }));
    setTimeout(() => {
      setStatuses(prev => ({ ...prev, [id]: 'connected' }));
    }, 1000);
  };

  const handleUploadFile = async (file: File) => {
    setIsParsing(true);
    setUploadError(null);
    setUploadedFileName(file.name);
    try {
      const response = await submitIntake(file);
      setVerdict(response.verdict);
      setChecks(response.checks);
      
      if ((response as any).business_id) {
        localStorage.setItem('active_business_id', (response as any).business_id);
      }
      
      addAuditEvent({
        type: 'intake',
        business_id: (response as any).business_id || 'CUST-NEW',
        business_name: file.name.replace(".csv", "").replace("_", " ").title ? file.name.replace(".csv", "").replace("_", " ") : 'Custom MSME Registration',
        summary: `Compliance verification result: ${response.verdict} (${response.checks.filter(c => c.status === 'pass').length}/${response.checks.length} passed)`
      });
    } catch (e) {
      setUploadError('Intake validation request failed. Check that the backend is running on port 8000, then upload again.');
    } finally {
      setIsParsing(false);
    }
  };

  const handlePresetSelect = async (presetType: 'green' | 'yellow' | 'red') => {
    let csvContent = "";
    let fileName = "";
    
    if (presetType === 'green') {
      csvContent = generateBankCSV(12, 20, true);
      fileName = "surat_silk_sarees_bank_statement.csv";
    } else if (presetType === 'yellow') {
      csvContent = generateBankCSV(12, 10, true);
      fileName = "royal_hyderabadi_biryani_bank_statement.csv";
    } else {
      csvContent = generateBankCSV(4, 18, false);
      fileName = "chennai_metal_components_bank_statement.csv";
    }

    const file = new File([csvContent], fileName, { type: "text/csv" });
    handleUploadFile(file);
  };

  const handleCustomFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleUploadFile(e.target.files[0]);
    }
  };

  const confirmBankConnection = () => {
    setStatuses(prev => ({ ...prev, bank: 'connected' }));
    setIsUploaderOpen(false);
    setVerdict(null);
    setChecks([]);
    setUploadedFileName('');
  };

  const closeUploader = () => {
    setIsUploaderOpen(false);
    setVerdict(null);
    setChecks([]);
    setUploadedFileName('');
    setUploadError(null);
  };

  const connectedCount = Object.values(statuses).filter(s => s === 'connected').length;

  return (
    <div className="min-h-screen flex flex-col bg-background font-sans selection:bg-primary selection:text-white">
      <nav className="sticky top-0 z-50 bg-white border-b border-border">
        <div className="max-w-[1440px] mx-auto px-6 lg:px-12 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary rounded flex items-center justify-center">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <span className="font-semibold text-lg text-primary tracking-tight">MSME360 CreditPulse</span>
          </div>
        </div>
      </nav>
      
      <main className="flex-grow flex flex-col items-center">
        <AnimatePresence mode="wait">
          {!isAnalyzing ? (
            <motion.div 
              key="connection-view"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
              className="w-full flex-grow flex flex-col"
            >
              <div className="w-full max-w-[1440px] mx-auto px-6 lg:px-12 py-8 flex-grow">
                <div className="mb-8 max-w-3xl">
                  <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-white border border-border rounded-full text-xs font-medium text-text-secondary mb-4 shadow-sm">
                    <ShieldCheck className="w-4 h-4 text-success" />
                    IDBI Institutional grade security
                  </div>
                  <h1 className="text-2xl md:text-3xl font-semibold text-text-primary mb-2">Connect Your Alternate Financial Data</h1>
                  <p className="text-sm text-text-secondary">Securely connect bank statements, GST filins, EPFO, and utility sources. Alternate data allows AI to compute dynamic risk ratings for faster underwriting.</p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                  {DATA_SOURCES.map((source) => (
                    <IntegrationCard 
                      key={source.id} 
                      source={source} 
                      status={statuses[source.id]} 
                      onConnect={() => handleConnect(source.id)} 
                    />
                  ))}
                </div>
              </div>

              <div className="sticky bottom-0 bg-white border-t border-border mt-auto z-40 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
                <div className="max-w-[1440px] mx-auto px-6 lg:px-12 h-20 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="flex flex-col">
                      <span className="text-sm font-semibold text-text-primary">{connectedCount} Sources Connected</span>
                      <span className="text-xs text-text-secondary">Connecting bank statements is required</span>
                    </div>
                  </div>
                  <button 
                    onClick={() => setIsAnalyzing(true)}
                    disabled={statuses.bank !== 'connected'}
                    className="bg-primary hover:bg-primary-hover text-white px-8 py-2.5 rounded font-medium flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                  >
                    Start Financial Assessment <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </motion.div>
          ) : (
            <motion.div 
              key="analysis-view"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3 }}
              className="w-full flex-grow flex items-center justify-center bg-background"
            >
              <AnalysisWorkflow />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Bank statement document compliance intake modal */}
      {isUploaderOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-xs">
          <div className="relative w-full max-w-2xl rounded-card border border-border bg-white shadow-2xl p-6 flex flex-col max-h-[90vh]">
            <div className="flex items-center justify-between pb-4 border-b border-border mb-4">
              <div>
                <h3 className="text-lg font-bold text-text-primary">Connect Bank Statements</h3>
                <p className="text-xs text-text-secondary">Verify statement structure, transaction coverage, and balancing compliance</p>
              </div>
              <button
                onClick={closeUploader}
                aria-label="Close bank statement uploader"
                className="rounded-lg p-1 text-text-secondary hover:bg-background-muted hover:text-text-primary transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" aria-hidden="true" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto space-y-6">
              
              {/* Presets Zone */}
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-text-secondary uppercase tracking-wider">Demo Scenario Templates</h4>
                <div className="grid grid-cols-3 gap-3">
                  <button
                    onClick={() => handlePresetSelect('green')}
                    className="p-3 border border-border hover:border-success bg-white hover:bg-success/5 rounded text-left transition-all cursor-pointer"
                  >
                    <div className="w-2 h-2 rounded-full bg-success mb-2" />
                    <p className="text-xs font-bold text-text-primary">Surat Silk Sarees</p>
                    <p className="text-[10px] text-text-secondary">Green verdict (Standard pass)</p>
                  </button>
                  <button
                    onClick={() => handlePresetSelect('yellow')}
                    className="p-3 border border-border hover:border-warning bg-white hover:bg-warning/5 rounded text-left transition-all cursor-pointer"
                  >
                    <div className="w-2 h-2 rounded-full bg-warning mb-2" />
                    <p className="text-xs font-bold text-text-primary">Royal Hyderabadi</p>
                    <p className="text-[10px] text-text-secondary">Yellow verdict (Low credits warning)</p>
                  </button>
                  <button
                    onClick={() => handlePresetSelect('red')}
                    className="p-3 border border-border hover:border-error bg-white hover:bg-error/5 rounded text-left transition-all cursor-pointer"
                  >
                    <div className="w-2 h-2 rounded-full bg-error mb-2" />
                    <p className="text-xs font-bold text-text-primary">Chennai Metals</p>
                    <p className="text-[10px] text-text-secondary">Red verdict (Reconciliation fails)</p>
                  </button>
                </div>
              </div>

              {/* Upload Drop Zone */}
              <div className="border-2 border-dashed border-border rounded p-6 flex flex-col items-center justify-center bg-background-muted/20 hover:bg-background-muted/40 transition-colors relative">
                <Upload className="w-8 h-8 text-primary mb-2" />
                <p className="text-xs font-semibold text-text-primary">Drag & Drop statement CSV or click to select</p>
                <p className="text-[10px] text-text-secondary mt-1">Accepts standard banking format CSVs (Date, Credit, Debit, Balance)</p>
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleCustomFileInput}
                  className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
                />
              </div>

              {uploadedFileName && (
                <div className="p-3 rounded bg-background-muted border border-border flex items-center justify-between text-xs">
                  <span className="font-semibold text-text-primary">{uploadedFileName}</span>
                  {isParsing && <Loader2 className="w-4 h-4 text-primary animate-spin" aria-label="Validating statement" />}
                </div>
              )}

              {uploadError && (
                <div role="alert" className="p-4 bg-error/10 border border-error/20 rounded text-error flex items-start gap-2.5">
                  <XCircle className="w-5 h-5 shrink-0 mt-0.5" aria-hidden="true" />
                  <div>
                    <h5 className="font-bold text-sm">Validation request failed</h5>
                    <p className="text-xs text-error/80 mt-0.5">{uploadError}</p>
                  </div>
                </div>
              )}

              {/* Parsing Compliance Checks Output */}
              {verdict && (
                <div className="space-y-4 pt-4 border-t border-border">
                  
                  {/* Verdict Banner */}
                  {verdict === 'GREEN' && (
                    <div className="p-4 bg-success/10 border border-success/20 rounded text-success flex items-start gap-2.5">
                      <CheckCircle2 className="w-5 h-5 shrink-0 mt-0.5" />
                      <div>
                        <h5 className="font-bold text-sm">Readiness Verdict: Compliant</h5>
                        <p className="text-xs text-success/80 mt-0.5">All policy rules met. The statement data is fully scorable.</p>
                      </div>
                    </div>
                  )}

                  {verdict === 'YELLOW' && (
                    <div className="p-4 bg-warning/10 border border-warning/20 rounded text-warning flex items-start gap-2.5">
                      <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
                      <div>
                        <h5 className="font-bold text-sm">Readiness Verdict: Scorable with warning</h5>
                        <p className="text-xs text-warning/80 mt-0.5">Minor anomalies detected. Scorable, but review checks below.</p>
                      </div>
                    </div>
                  )}

                  {verdict === 'RED' && (
                    <div className="p-4 bg-error/10 border border-error/20 rounded text-error flex items-start gap-2.5">
                      <XCircle className="w-5 h-5 shrink-0 mt-0.5" />
                      <div>
                        <h5 className="font-bold text-sm">Readiness Verdict: Non-Compliant</h5>
                        <p className="text-xs text-error/80 mt-0.5">Critical compliance rules failed. Scoring is currently blocked.</p>
                      </div>
                    </div>
                  )}

                  {/* Checklist */}
                  <div className="space-y-2">
                    <h5 className="text-xs font-bold text-text-secondary uppercase">Compliance Checks</h5>
                    <div className="divide-y divide-border border border-border rounded overflow-hidden">
                      {checks.map((c, idx) => (
                        <div key={idx} className="p-3 flex items-start justify-between gap-3 text-xs bg-white">
                          <div>
                            <p className="font-semibold text-text-primary">{c.name}</p>
                            <p className="text-text-secondary text-[11px] mt-0.5">{c.desc}</p>
                            {c.message && (
                              <p className={`mt-1 font-medium ${c.status === 'fail' ? 'text-error' : c.status === 'warn' ? 'text-warning' : 'text-success'}`}>
                                {c.message}
                              </p>
                            )}
                          </div>
                          <div>
                            {c.status === 'pass' && <CheckCircle2 className="w-4.5 h-4.5 text-success" />}
                            {c.status === 'warn' && <AlertCircle className="w-4.5 h-4.5 text-warning" />}
                            {c.status === 'fail' && <XCircle className="w-4.5 h-4.5 text-error" />}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                </div>
              )}

            </div>

            {/* Modal Footer */}
            <div className="flex justify-end gap-3 pt-4 border-t border-border mt-auto">
              <button
                onClick={closeUploader}
                className="px-4 py-2 border border-border hover:bg-background-muted text-text-primary text-sm font-semibold rounded cursor-pointer transition-colors"
              >
                Cancel
              </button>
              <button
                disabled={verdict === 'RED' || !verdict}
                onClick={confirmBankConnection}
                className="px-4 py-2 bg-primary hover:bg-primary-hover disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-semibold rounded cursor-pointer transition-colors"
              >
                Confirm Connection
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
