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
  Loader2,
  ArrowRight,
  ShieldCheck
} from 'lucide-react';

type ConnectionStatus = 'disconnected' | 'connecting' | 'connected';

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
  { id: 'bank', name: 'Bank Statements', description: 'Upload PDF statements securely', icon: <ScrollText className="w-6 h-6" /> },
  { id: 'itr', name: 'Income Tax Returns', description: 'ITR-3 / ITR-4 acknowledgments', icon: <Receipt className="w-6 h-6" /> },
  { id: 'utility', name: 'Utility Bills', description: 'Electricity & broadband payment history', icon: <Lightbulb className="w-6 h-6" /> },
  { id: 'invoices', name: 'Sales Invoices', description: 'ERP or accounting software sync', icon: <FileStack className="w-6 h-6" /> },
];

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
            className="w-full py-2 bg-white border border-border rounded text-sm font-medium text-text-primary hover:bg-background-muted transition-colors"
            onClick={onConnect}
          >
            Manage Connection
          </button>
        ) : (
          <button 
            disabled={status === 'connecting'}
            className="w-full py-2 bg-primary hover:bg-primary-hover text-white rounded text-sm font-medium transition-colors disabled:opacity-70 disabled:cursor-not-allowed"
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

  const handleConnect = (id: string) => {
    if (statuses[id] === 'connected') {
      setStatuses(prev => ({ ...prev, [id]: 'disconnected' }));
      return;
    }
    setStatuses(prev => ({ ...prev, [id]: 'connecting' }));
    setTimeout(() => {
      setStatuses(prev => ({ ...prev, [id]: 'connected' }));
    }, 1000);
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
            <span className="font-semibold text-lg text-primary tracking-tight">CreditPulse AI</span>
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
                    Bank-grade 256-bit encryption
                  </div>
                  <h1 className="text-2xl md:text-3xl font-semibold text-text-primary mb-2">Connect Your Financial Data</h1>
                  <p className="text-sm text-text-secondary">Securely connect alternate financial data sources. More connected sources yield a highly accurate assessment and better loan recommendations.</p>
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
                      <span className="text-xs text-text-secondary">Minimum 2 recommended</span>
                    </div>
                  </div>
                  <button 
                    onClick={() => setIsAnalyzing(true)}
                    className="bg-primary hover:bg-primary-hover text-white px-8 py-2.5 rounded font-medium flex items-center gap-2 transition-colors disabled:opacity-50"
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
    </div>
  );
}
