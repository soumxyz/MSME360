import React, { useState, useEffect } from 'react';
import { motion as framerMotion, AnimatePresence as FramerAnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { 
  Activity, FileText, Smartphone, Landmark, Briefcase, 
  CheckCircle2, AlertCircle, Loader2, ArrowRight, ShieldCheck, ArrowLeft, Building2
} from 'lucide-react';

type ConnectionStatus = 'disconnected' | 'connecting' | 'connected';

interface WizardStep {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  infoLabel: string;
}

const WIZARD_STEPS: WizardStep[] = [
  { 
    id: 'gst', 
    name: 'Connect GST Returns', 
    description: 'We fetch authorized GSTR-1 and GSTR-3B filings to verify historical turnover, seasonality, and digital adoption velocity.',
    icon: <FileText className="w-12 h-12 text-primary" />,
    infoLabel: 'Direct GSTN Consent integration'
  },
  { 
    id: 'aa', 
    name: 'Connect Account Aggregator', 
    description: 'Provide consent to securely aggregate bank statement data in real-time to analyze average monthly balances and credit velocity.',
    icon: <Landmark className="w-12 h-12 text-primary" />,
    infoLabel: 'FIP-certified secure aggregation'
  },
  { 
    id: 'upi', 
    name: 'Connect UPI Transactions', 
    description: 'Verify retail merchant QR inflows and VPA velocity to evaluate short-term working capital cycles.',
    icon: <Smartphone className="w-12 h-12 text-primary" />,
    infoLabel: 'NPCI UPI network validation'
  }
];

const AnalysisWorkflow = ({ businessName, businessType, loanRequested }: any) => {
  const [currentStep, setCurrentStep] = useState(0);
  const navigate = useNavigate();

  const steps = [
    { title: "Initializing AI Credit Workspace", desc: "Setting up CreditPilot AI multi-agent workspace." },
    { title: "Agent 1: Financial Intelligence Agent", desc: "Analyzing GST, AA, and UPI cash flow metrics." },
    { title: "Agent 2: Risk & Compliance Agent", desc: "Running RBI policy checks and anomaly/fraud pattern validations." },
    { title: "Agent 3: AI Credit Copilot", desc: "Synthesizing agent inputs to generate explainable recommendations." },
    { title: "Compiling Credit Assessment Report", desc: "Finalizing dashboard underwriting profiles." }
  ];

  useEffect(() => {
    // Start real-time API call to backend
    const triggerEvaluation = async () => {
      try {
        const response = await fetch('/api/v1/evaluate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer mock-token'
          },
          body: JSON.stringify({
            "msme_id": "MSME_2024_001",
            "pan": "ABCDE1234F",
            "gst_data": {
              "gstin": "27ABCDE1234F1Z5",
              "registration_date": "2022-01-15",
              "monthly_returns": [
                {"month": "2023-01", "revenue": 450000, "filed": true},
                {"month": "2023-02", "revenue": 480000, "filed": true},
                {"month": "2023-03", "revenue": 510000, "filed": true},
                {"month": "2023-04", "revenue": 490000, "filed": true},
                {"month": "2023-05", "revenue": 520000, "filed": true},
                {"month": "2023-06", "revenue": 540000, "filed": true},
                {"month": "2023-07", "revenue": 560000, "filed": true},
                {"month": "2023-08", "revenue": 580000, "filed": true},
                {"month": "2023-09", "revenue": 600000, "filed": true},
                {"month": "2023-10", "revenue": 620000, "filed": true},
                {"month": "2023-11", "revenue": 640000, "filed": true},
                {"month": "2023-12", "revenue": 660000, "filed": true}
              ],
              "filing_history": {
                "total_filings_due": 12,
                "filings_completed": 12,
                "filings_missed": 0
              }
            },
            "upi_data": {
              "transactions": [
                {"transaction_id": "UPI001", "timestamp": "2024-01-15T10:30:00Z", "amount": 15000.50, "counterparty": "VENDOR_A", "type": "debit"},
                {"transaction_id": "UPI002", "timestamp": "2024-01-16T14:20:00Z", "amount": 25000.00, "counterparty": "CLIENT_B", "type": "credit"},
                {"transaction_id": "UPI003", "timestamp": "2024-01-17T09:15:00Z", "amount": 8500.75, "counterparty": "VENDOR_C", "type": "debit"},
                {"transaction_id": "UPI004", "timestamp": "2024-01-18T16:45:00Z", "amount": 35000.00, "counterparty": "CLIENT_D", "type": "credit"},
                {"transaction_id": "UPI005", "timestamp": "2024-01-19T11:30:00Z", "amount": 12000.25, "counterparty": "VENDOR_E", "type": "debit"},
                {"transaction_id": "UPI006", "timestamp": "2024-02-15T10:30:00Z", "amount": 18000.00, "counterparty": "VENDOR_A", "type": "debit"},
                {"transaction_id": "UPI007", "timestamp": "2024-02-16T14:20:00Z", "amount": 28000.00, "counterparty": "CLIENT_B", "type": "credit"},
                {"transaction_id": "UPI008", "timestamp": "2024-03-15T10:30:00Z", "amount": 16000.00, "counterparty": "VENDOR_F", "type": "debit"},
                {"transaction_id": "UPI009", "timestamp": "2024-03-16T14:20:00Z", "amount": 30000.00, "counterparty": "CLIENT_G", "type": "credit"},
                {"transaction_id": "UPI010", "timestamp": "2024-04-15T10:30:00Z", "amount": 17000.00, "counterparty": "VENDOR_H", "type": "debit"}
              ],
              "summary": {
                "total_transactions": 10,
                "total_volume": 204501.50,
                "period_start": "2024-01-01",
                "period_end": "2024-04-30"
              }
            },
            "account_aggregator_data": {
              "monthly_statements": [
                {"month": "2023-11", "opening_balance": 850000, "closing_balance": 920000, "total_credits": 650000, "total_debits": 580000},
                {"month": "2023-12", "opening_balance": 920000, "closing_balance": 980000, "total_credits": 680000, "total_debits": 620000},
                {"month": "2024-01", "opening_balance": 980000, "closing_balance": 1050000, "total_credits": 720000, "total_debits": 650000},
                {"month": "2024-02", "opening_balance": 1050000, "closing_balance": 1120000, "total_credits": 750000, "total_debits": 680000},
                {"month": "2024-03", "opening_balance": 1120000, "closing_balance": 1200000, "total_credits": 800000, "total_debits": 720000},
                {"month": "2024-04", "opening_balance": 1200000, "closing_balance": 1280000, "total_credits": 850000, "total_debits": 770000}
              ]
            },
            "epfo_data": {
              "monthly_records": [
                {"month": "2023-01", "employee_count": 12},
                {"month": "2023-02", "employee_count": 12},
                {"month": "2023-03", "employee_count": 13},
                {"month": "2023-04", "employee_count": 13},
                {"month": "2023-05", "employee_count": 14},
                {"month": "2023-06", "employee_count": 14},
                {"month": "2023-07", "employee_count": 15},
                {"month": "2023-08", "employee_count": 15},
                {"month": "2023-09", "employee_count": 16},
                {"month": "2023-10", "employee_count": 16},
                {"month": "2023-11", "employee_count": 17},
                {"month": "2023-12", "employee_count": 18}
              ]
            },
            "bank_data": {
              "monthly_emi": 45000,
              "outstanding_loan": 1500000,
              "loan_to_turnover_ratio": 0.25,
              "statement_start_date": "2024-01-01",
              "statement_end_date": "2024-04-30"
            }
          })
        });
        
        if (!response.ok) throw new Error("API status failed");
        
        const report = await response.json();
        localStorage.setItem('assessment_report', JSON.stringify(report));

        // Save real-time application record to list
        const defaultApps = [
          { id: 'APP-10294', name: 'ABC Manufacturing', type: 'Manufacturing', status: 'Pending Review', risk: 'Medium', loan: '₹20,00,000' },
          { id: 'APP-10295', name: 'XYZ Traders', type: 'Retail & Commerce', status: 'High Risk', risk: 'High', loan: '₹15,00,000' },
          { id: 'APP-10296', name: 'Sharma Electronics', type: 'Electronics Dealership', status: 'Approved', risk: 'Low', loan: '₹35,00,000' },
          { id: 'APP-10297', name: 'Kumar Textiles', type: 'Apparel Mfg', status: 'Pending Review', risk: 'Medium', loan: '₹25,00,000' },
        ];
        const stored = localStorage.getItem('all_applications');
        const currentApps = stored ? JSON.parse(stored) : defaultApps;

        const newApp = {
          id: 'APP-' + Math.floor(10000 + Math.random() * 9000),
          name: businessName || 'Acme Industries Pvt Ltd',
          type: businessType || 'Manufacturing',
          status: 'Pending Review',
          risk: report.risk_category || 'Medium',
          loan: '₹' + Number(loanRequested || 2000000).toLocaleString('en-IN')
        };
        
        localStorage.setItem('all_applications', JSON.stringify([newApp, ...currentApps]));
      } catch (err) {
        console.error("Failed to run real-time assessment: ", err);
      }
    };
    triggerEvaluation();
  }, [businessName, businessType, loanRequested]);

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
      <framerMotion.div 
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
            <framerMotion.div 
              className="h-full bg-primary"
              initial={{ width: 0 }}
              animate={{ width: `${(currentStep / steps.length) * 100}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>

      </framerMotion.div>
    </div>
  );
};

export default function BusinessRegistration() {
  const [activeStep, setActiveStep] = useState(0); // Step 0 = Basic Info Form
  
  // Basic Business Info form fields
  const [businessName, setBusinessName] = useState('');
  const [ownerName, setOwnerName] = useState('');
  const [pan, setPan] = useState('');
  const [loanRequested, setLoanRequested] = useState('');
  const [businessType, setBusinessType] = useState('Manufacturing');

  const [statuses, setStatuses] = useState<Record<string, ConnectionStatus>>({
    gst: 'disconnected',
    aa: 'disconnected',
    upi: 'disconnected'
  });
  
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const autoConnect = (id: string) => {
    setStatuses(prev => ({ ...prev, [id]: 'connecting' }));
    setTimeout(() => {
      setStatuses(prev => ({ ...prev, [id]: 'connected' }));
    }, 1500); // 1.5s animation
  };

  const handleConnect = (id: string) => {
    if (statuses[id] === 'connected') {
      setStatuses(prev => ({ ...prev, [id]: 'disconnected' }));
      return;
    }
    autoConnect(id);
  };

  // Automatically start connecting when steps 1, 2, or 3 mount
  useEffect(() => {
    if (activeStep > 0 && activeStep <= WIZARD_STEPS.length) {
      const source = WIZARD_STEPS[activeStep - 1];
      if (statuses[source.id] === 'disconnected') {
        const timer = setTimeout(() => {
          autoConnect(source.id);
        }, 600);
        return () => clearTimeout(timer);
      }
    }
  }, [activeStep]);

  const currentSource = activeStep > 0 && activeStep <= WIZARD_STEPS.length ? WIZARD_STEPS[activeStep - 1] : null;
  const isCurrentStepConnected = currentSource && statuses[currentSource.id] === 'connected';

  // Enable Next button validation for step 0
  const isBasicInfoValid = businessName.trim() !== '' && pan.trim() !== '' && loanRequested.trim() !== '';

  return (
    <div className="min-h-screen flex flex-col bg-background font-sans selection:bg-primary selection:text-white">
      <nav className="sticky top-0 z-50 bg-white border-b border-border">
        <div className="max-w-[1440px] mx-auto px-6 lg:px-12 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary rounded flex items-center justify-center">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <span className="font-semibold text-lg text-primary tracking-tight">CreditPulse AI</span>
          </div>
        </div>
      </nav>
      
      <main className="flex-grow flex flex-col items-center">
        <FramerAnimatePresence mode="wait">
          {!isAnalyzing ? (
            <framerMotion.div 
              key="connection-view"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
              className="w-full flex-grow flex flex-col max-w-3xl mx-auto px-6 py-12"
            >
              {/* Stepper Progress Indicator */}
              <div className="flex items-center justify-between mb-10 border-b border-border pb-6">
                <div className="flex items-center gap-2">
                  <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                    activeStep > 0 ? 'bg-success text-white' : 'bg-primary text-white ring-4 ring-primary/20'
                  }`}>
                    1
                  </div>
                  <span className={`text-xs font-semibold ${activeStep === 0 ? 'text-primary' : 'text-success'}`}>
                    Basic Information
                  </span>
                </div>
                <div className="w-8 h-[1px] bg-border mx-2 hidden md:block" />

                {WIZARD_STEPS.map((step, idx) => {
                  const stepIdx = idx + 1;
                  const isPast = stepIdx < activeStep;
                  const isCurrent = stepIdx === activeStep;
                  return (
                    <div key={step.id} className="flex items-center gap-2">
                      <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                        isPast 
                          ? 'bg-success text-white' 
                          : isCurrent 
                          ? 'bg-primary text-white ring-4 ring-primary/20' 
                          : 'bg-background-muted text-text-secondary border border-border'
                      }`}>
                        {isPast ? '✓' : stepIdx + 1}
                      </div>
                      <span className={`text-xs font-semibold hidden md:inline ${
                        isCurrent ? 'text-primary' : isPast ? 'text-success' : 'text-text-secondary'
                      }`}>
                        {step.id.toUpperCase()} Connection
                      </span>
                      {stepIdx < WIZARD_STEPS.length && (
                        <div className="w-8 h-[1px] bg-border mx-2 hidden md:block" />
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Dynamic Connection View */}
              {activeStep === 0 ? (
                // Step 0: Basic Info Form
                <framerMotion.div
                  key="basic-info-form"
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-white border border-border rounded-card p-8 md:p-12 shadow-card space-y-6"
                >
                  <div className="flex items-center gap-3 pb-4 border-b border-border">
                    <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center text-primary">
                      <Building2 className="w-5 h-5" />
                    </div>
                    <div>
                      <h2 className="text-lg font-bold text-text-primary">Business Profile Setup</h2>
                      <p className="text-xs text-text-secondary">Provide structural parameters to initialize assessment algorithms.</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
                    <div>
                      <label className="block font-bold text-text-primary uppercase tracking-wider mb-2">Registered Business Name</label>
                      <input 
                        type="text" 
                        placeholder="e.g. Acme Industries Pvt Ltd"
                        value={businessName}
                        onChange={(e) => setBusinessName(e.target.value)}
                        className="w-full p-2.5 border border-border bg-white rounded focus:outline-none focus:border-primary"
                      />
                    </div>
                    <div>
                      <label className="block font-bold text-text-primary uppercase tracking-wider mb-2">Owner Full Name</label>
                      <input 
                        type="text" 
                        placeholder="e.g. Priya Sharma"
                        value={ownerName}
                        onChange={(e) => setOwnerName(e.target.value)}
                        className="w-full p-2.5 border border-border bg-white rounded focus:outline-none focus:border-primary"
                      />
                    </div>
                    <div>
                      <label className="block font-bold text-text-primary uppercase tracking-wider mb-2">Business PAN ID</label>
                      <input 
                        type="text" 
                        maxLength={10}
                        placeholder="e.g. ABCDE1234F"
                        value={pan}
                        onChange={(e) => setPan(e.target.value)}
                        className="w-full p-2.5 border border-border bg-white rounded focus:outline-none focus:border-primary uppercase"
                      />
                    </div>
                    <div>
                      <label className="block font-bold text-text-primary uppercase tracking-wider mb-2">Loan Amount Required (INR)</label>
                      <input 
                        type="number" 
                        placeholder="e.g. 2000000"
                        value={loanRequested}
                        onChange={(e) => setLoanRequested(e.target.value)}
                        className="w-full p-2.5 border border-border bg-white rounded focus:outline-none focus:border-primary"
                      />
                    </div>
                    <div>
                      <label className="block font-bold text-text-primary uppercase tracking-wider mb-2">Sectors classification</label>
                      <select
                        value={businessType}
                        onChange={(e) => setBusinessType(e.target.value)}
                        className="w-full p-2.5 border border-border bg-white rounded focus:outline-none focus:border-primary"
                      >
                        <option value="Manufacturing">Manufacturing & Engineering</option>
                        <option value="Retail & Commerce">Retail & Wholesale Commerce</option>
                        <option value="Electronics Dealership">Electronics Dealership</option>
                        <option value="Apparel Mfg">Apparel Manufacturing</option>
                      </select>
                    </div>
                  </div>
                </framerMotion.div>
              ) : activeStep <= WIZARD_STEPS.length ? (
                // Steps 1 to 3: Connections
                <framerMotion.div
                  key={currentSource!.id}
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-white border border-border rounded-card p-8 md:p-12 shadow-card flex flex-col items-center text-center"
                >
                  <div className="w-20 h-20 bg-primary/5 rounded-full flex items-center justify-center mb-6 border border-primary/10">
                    {currentSource!.icon}
                  </div>
                  
                  <span className="text-[10px] bg-success/15 text-success border border-success/20 font-bold px-3 py-1 rounded-full mb-3 flex items-center gap-1">
                    <ShieldCheck className="w-3.5 h-3.5" /> {currentSource!.infoLabel}
                  </span>

                  <h2 className="text-xl font-bold text-text-primary mb-3">{currentSource!.name}</h2>
                  <p className="text-sm text-text-secondary max-w-md mb-8 leading-relaxed">
                    {currentSource!.description}
                  </p>

                  <div className="w-full max-w-xs space-y-4">
                    {statuses[currentSource!.id] === 'connected' ? (
                      <div className="p-3 border border-success bg-success/5 rounded flex items-center justify-center gap-2 text-success font-semibold text-sm">
                        <CheckCircle2 className="w-4 h-4" /> Connected Successfully
                      </div>
                    ) : statuses[currentSource!.id] === 'connecting' ? (
                      <button 
                        disabled 
                        className="w-full py-3 bg-warning text-white rounded font-medium text-sm flex items-center justify-center gap-2"
                      >
                        <Loader2 className="w-4 h-4 animate-spin" /> Fetching Authorization...
                      </button>
                    ) : (
                      <button 
                        onClick={() => handleConnect(currentSource!.id)}
                        className="w-full py-3 bg-primary hover:bg-primary-hover text-white rounded font-semibold text-sm transition-colors shadow-sm"
                      >
                        Consent & Connect
                      </button>
                    )}
                  </div>
                </framerMotion.div>
              ) : (
                // Final submission summary view
                <framerMotion.div 
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-white border border-border rounded-card p-8 md:p-12 shadow-card"
                >
                  <h2 className="text-xl font-bold text-text-primary mb-2 text-center">Ready to Assess Financial Health</h2>
                  <p className="text-xs text-text-secondary text-center mb-8">All required consent channels have been configured successfully.</p>
                  
                  <div className="space-y-4 max-w-md mx-auto mb-10">
                    <div className="p-4 border border-border rounded-card flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="text-xs font-semibold text-text-secondary uppercase">Applicant profile:</span>
                        <span className="text-xs font-bold text-text-primary">{businessName}</span>
                      </div>
                    </div>
                    {WIZARD_STEPS.map((step) => (
                      <div key={step.id} className="p-4 border border-border rounded-card flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <CheckCircle2 className="w-5 h-5 text-success" />
                          <span className="text-xs font-bold text-text-primary">{step.name}</span>
                        </div>
                        <span className="text-[10px] font-bold text-success uppercase">Active</span>
                      </div>
                    ))}
                  </div>

                  <div className="flex justify-center">
                    <button 
                      onClick={() => setIsAnalyzing(true)}
                      className="bg-primary hover:bg-primary-hover text-white px-8 py-3 rounded-card font-semibold text-sm flex items-center gap-2 transition-colors shadow-sm"
                    >
                      Start Financial Assessment <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                </framerMotion.div>
              )}

              {/* Navigation Back / Next Toggles */}
              <div className="flex items-center justify-between mt-10">
                <button
                  disabled={activeStep === 0}
                  onClick={() => setActiveStep(prev => prev - 1)}
                  className="px-4 py-2 border border-border rounded text-xs font-semibold text-text-secondary hover:bg-background-muted transition-colors disabled:opacity-30 disabled:cursor-not-allowed flex items-center gap-1.5"
                >
                  <ArrowLeft className="w-3.5 h-3.5" /> Back
                </button>
                {activeStep <= WIZARD_STEPS.length && (
                  <button
                    disabled={activeStep === 0 ? !isBasicInfoValid : !isCurrentStepConnected}
                    onClick={() => setActiveStep(prev => prev + 1)}
                    className="px-5 py-2 bg-primary hover:bg-primary-hover text-white rounded text-xs font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1.5"
                  >
                    Next Connection <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            </framerMotion.div>
          ) : (
            <framerMotion.div 
              key="analysis-view"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3 }}
              className="w-full flex-grow flex items-center justify-center bg-background"
            >
              <AnalysisWorkflow 
                businessName={businessName}
                businessType={businessType}
                loanRequested={loanRequested}
              />
            </framerMotion.div>
          )}
        </FramerAnimatePresence>
      </main>
    </div>
  );
}
