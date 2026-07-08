import React, { useState, useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
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
  ArrowLeft,
  ShieldCheck,
  Upload,
  X,
  Building2,
  HelpCircle,
  Check,
  BrainCircuit,
  FileSpreadsheet,
  Camera,
  Sparkles,
  Info
} from 'lucide-react';
import { registerMSME, extractDocument } from '../lib/api';
import type { OcrExtractResult } from '../lib/api';
import { formatINR } from '../lib/format';

const steps = [
  { title: "Aggregating Digital Consents", desc: "Financial Intelligence Agent is securely fetching records from GSTN, EPFO, and UPI networks." },
  { title: "Normalizing Financial Accounts", desc: "Financial Intelligence Agent is structuring bank ledger transactions and computing operational cash flows." },
  { title: "Verifying Risk & Compliance", desc: "Risk & Compliance Agent is validating PAN/Aadhaar/Udyam registries and running fraud detection heuristics." },
  { title: "Compiling Financial Health Card", desc: "CreditPilot AI is scoring cash-buffer days, revenue growth stability, and digital payment ratios." },
  { title: "Formulating Pre-Qualified Loan Offers", desc: "CreditPilot AI is mapping your dynamic score to IDBI Bank institutional credit limits." }
];

const slideVariants = {
  enter: (direction: number) => ({
    x: direction > 0 ? 100 : -100,
    opacity: 0
  }),
  center: {
    x: 0,
    opacity: 1,
    transition: { duration: 0.35, ease: "easeInOut" as const }
  },
  exit: (direction: number) => ({
    x: direction < 0 ? 100 : -100,
    opacity: 0,
    transition: { duration: 0.3, ease: "easeInOut" as const }
  })
};

const AnalysisWorkflow = ({ businessId: _businessId }: { businessId: string }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    if (currentStep < steps.length) {
      const timer = setTimeout(() => {
        setCurrentStep(prev => prev + 1);
      }, 1800);
      return () => clearTimeout(timer);
    } else {
      // Client-side navigation preserves the freshly-warmed react-query cache;
      // the previous `window.location.href` triggered a full page reload.
      const timer = setTimeout(() => {
        navigate('/customer/dashboard');
      }, 800);
      return () => clearTimeout(timer);
    }
  }, [currentStep, navigate]);

  return (
    <div className="w-full max-w-2xl mx-auto py-12 px-4">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-panel p-8 md:p-12 shadow-primary/10"
      >
        <div className="text-center mb-10">
          <div className="w-16 h-16 bg-primary-soft rounded-full flex items-center justify-center mx-auto mb-6 shadow-glow shadow-primary/20">
            <Activity className="w-8 h-8 text-primary animate-pulse-slow" />
          </div>
          <h2 className="text-2xl font-semibold text-text-primary mb-2">Analyzing Business Creditworthiness</h2>
          <p className="text-sm text-text-secondary">Please wait while our multi-agent AI system processes your application.</p>
        </div>

        <div className="space-y-6">
          {steps.map((step, index) => {
            const isActive = index === currentStep;
            const isCompleted = index < currentStep;
            const isPending = index > currentStep;

            return (
              <div key={index} className="flex items-start gap-4">
                <div className="mt-0.5">
                  {isCompleted && <CheckCircle2 className="w-5 h-5 text-[#008269]" />}
                  {isActive && <Loader2 className="w-5 h-5 text-[#008269] animate-spin" />}
                  {isPending && <div className="w-5 h-5 rounded-full border-2 border-border" />}
                </div>
                <div>
                  <h4 className={`text-sm font-semibold mb-0.5 ${isActive || isCompleted ? 'text-text-primary' : 'text-text-secondary'}`}>
                    {step.title}
                  </h4>
                  <p className="text-xs text-text-secondary leading-relaxed">{step.desc}</p>
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
              className="h-full bg-[#008269]"
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
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [currentStep, setCurrentStep] = useState(1);
  const [direction, setDirection] = useState(1);

  // 1. Basic Business Information (Manual Input)
  const [businessName, setBusinessName] = useState('');
  const [ownerName, setOwnerName] = useState('');
  const [mobileNumber, setMobileNumber] = useState('');
  const [email, setEmail] = useState('');
  const [panNumber, setPanNumber] = useState('');
  const [gstin, setGstin] = useState('');
  const [udyamNumber, setUdyamNumber] = useState('');
  const [businessType, setBusinessType] = useState('Sole Proprietor');
  const [industry, setIndustry] = useState('Manufacturing');
  const [yearsInBusiness, setYearsInBusiness] = useState('');
  const [loanAmount, setLoanAmount] = useState('');
  const [loanPurpose, setLoanPurpose] = useState('Working Capital');

  // 2. Digital Consent Connections (Toggles)
  const [connectGst, setConnectGst] = useState(false);
  const [connectAa, setConnectAa] = useState(false);
  const [connectUpi, setConnectUpi] = useState(false);
  const [connectEpfo, setConnectEpfo] = useState(false);

  // Connecting loaders
  const [connectingGst, setConnectingGst] = useState(false);
  const [connectingAa, setConnectingAa] = useState(false);
  const [connectingUpi, setConnectingUpi] = useState(false);
  const [connectingEpfo, setConnectingEpfo] = useState(false);

  // 3. Fallback File Uploads (Mock States)
  const [panFile, setPanFile] = useState<string | null>(null);
  const [aadhaarFile, setAadhaarFile] = useState<string | null>(null);
  const [udyamFile, setUdyamFile] = useState<string | null>(null);
  const [bankFile, setBankFile] = useState<string | null>(null);

  // Submission / Loading states
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [registeredId, setRegisteredId] = useState('');

  // OCR States
  const [isOcrLoading, setIsOcrLoading] = useState(false);
  const [ocrProgressText, setOcrProgressText] = useState("");
  const [ocrSuccess, setOcrSuccess] = useState<string | null>(null);
  const [ocrSource, setOcrSource] = useState<string | null>(null);
  const [ocrExtracted, setOcrExtracted] = useState<OcrExtractResult['extracted'] | null>(null);
  const [ocrFileName, setOcrFileName] = useState<string | null>(null);

  // Consent Sub-Step Animation States
  const [consentSubStep, setConsentSubStep] = useState(1);

  // Automatically trigger first connection when entering Step 2
  useEffect(() => {
    if (currentStep === 2) {
      if (consentSubStep === 1 && !connectGst && !connectingGst) {
        setConnectingGst(true);
        const t = setTimeout(() => {
          setConnectingGst(false);
          setConnectGst(true);
        }, 1500);
        return () => clearTimeout(t);
      }
    }
  }, [currentStep, consentSubStep]);

  const handleNextConsentSubStep = () => {
    if (consentSubStep === 1) {
      setConsentSubStep(2);
      setConnectingAa(true);
      setTimeout(() => {
        setConnectingAa(false);
        setConnectAa(true);
      }, 1500);
    } else if (consentSubStep === 2) {
      setConsentSubStep(3);
      setConnectingUpi(true);
      setTimeout(() => {
        setConnectingUpi(false);
        setConnectUpi(true);
      }, 1500);
    } else if (consentSubStep === 3) {
      setConsentSubStep(4);
      setConnectingEpfo(true);
      setTimeout(() => {
        setConnectingEpfo(false);
        setConnectEpfo(true);
      }, 1500);
    } else {
      goToNextStep();
    }
  };

  const handlePrevConsentSubStep = () => {
    if (consentSubStep > 1) {
      if (consentSubStep === 2) { setConnectAa(false); setConsentSubStep(1); }
      else if (consentSubStep === 3) { setConnectUpi(false); setConsentSubStep(2); }
      else if (consentSubStep === 4) { setConnectEpfo(false); setConsentSubStep(3); }
    } else {
      goToPrevStep();
    }
  };

  const handleOcrFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const isCSV = file.name.toLowerCase().endsWith('.csv');
    const isImage = file.type.startsWith('image/');
    
    setIsOcrLoading(true);
    setOcrSuccess(null);
    setOcrSource(null);
    setOcrExtracted(null);
    setOcrFileName(file.name);

    if (isCSV) {
      setOcrProgressText("Parsing CSV bank statement structure...");
    } else {
      setOcrProgressText("Initializing Gemini Vision OCR Engine...");
    }

    try {
      // Brief delay for UX polish
      await new Promise(r => setTimeout(r, 600));
      setOcrProgressText(isCSV 
        ? "Extracting transaction data & computing financial metrics..."
        : "Scanning statement layout and extracting text blocks..."
      );

      const result = await extractDocument(file);
      const data = result.extracted;

      await new Promise(r => setTimeout(r, 400));
      setOcrProgressText("Mapping extracted fields to registration form...");
      await new Promise(r => setTimeout(r, 300));

      // Pre-fill form fields from extracted data
      if (data.business_name) setBusinessName(data.business_name);
      if (data.owner_name) setOwnerName(data.owner_name);
      if (data.pan_number) setPanNumber(data.pan_number);
      if (data.gstin) setGstin(data.gstin);
      if (data.industry_hint) {
        // Map industry hint to nearest select option
        const hint = data.industry_hint.toLowerCase();
        if (hint.includes('manufactur') || hint.includes('textile') || hint.includes('silk')) setIndustry('Manufacturing');
        else if (hint.includes('retail') || hint.includes('kirana') || hint.includes('store') || hint.includes('grocery')) setIndustry('Retail');
        else if (hint.includes('wholesale') || hint.includes('distribut')) setIndustry('Wholesale');
        else if (hint.includes('service')) setIndustry('Services');
        else if (hint.includes('logistic') || hint.includes('transport')) setIndustry('Logistics');
        else setIndustry('Others');
      }

      // Determine source label
      let sourceLabel = "AI Extraction";
      if (result.source === 'csv_parser') sourceLabel = "CSV Parser";
      else if (result.source === 'gemini_vision') sourceLabel = "Gemini Vision AI";
      else if (result.source === 'mock_fallback') sourceLabel = "Demo Mode (set GEMINI_API_KEY for live)";

      setOcrSource(sourceLabel);
      setOcrExtracted(data);
      setIsOcrLoading(false);

      const fieldCount = [data.business_name, data.owner_name, data.pan_number, data.gstin, data.industry_hint].filter(Boolean).length;
      setOcrSuccess(
        isCSV 
          ? `CSV Parsed! ${data.transaction_count ?? 0} transactions analyzed. ${fieldCount} fields pre-filled.`
          : `Vision Extraction Complete! ${fieldCount} fields pre-filled.`
      );
    } catch (err: any) {
      console.error('OCR extraction failed:', err);
      setIsOcrLoading(false);
      setOcrSuccess(null);
      setOcrSource(null);
      setErrorMsg(`Document extraction failed: ${err.message}`);
    }
  };

  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Consent toggles simulation
  const handleToggleConsent = (source: 'gst' | 'aa' | 'upi' | 'epfo') => {
    if (source === 'gst') {
      if (connectGst) { setConnectGst(false); return; }
      setConnectingGst(true);
      setTimeout(() => { setConnectingGst(false); setConnectGst(true); }, 1000);
    } else if (source === 'aa') {
      if (connectAa) { setConnectAa(false); return; }
      setConnectingAa(true);
      setTimeout(() => { setConnectingAa(false); setConnectAa(true); }, 1000);
    } else if (source === 'upi') {
      if (connectUpi) { setConnectUpi(false); return; }
      setConnectingUpi(true);
      setTimeout(() => { setConnectingUpi(false); setConnectUpi(true); }, 1000);
    } else if (source === 'epfo') {
      if (connectEpfo) { setConnectEpfo(false); return; }
      setConnectingEpfo(true);
      setTimeout(() => { setConnectingEpfo(false); setConnectEpfo(true); }, 1000);
    }
  };

  // Mock file uploads handler
  const handleMockUpload = (e: React.ChangeEvent<HTMLInputElement>, fileType: 'pan' | 'aadhaar' | 'udyam' | 'bank') => {
    if (e.target.files && e.target.files[0]) {
      const name = e.target.files[0].name;
      if (fileType === 'pan') setPanFile(name);
      else if (fileType === 'aadhaar') setAadhaarFile(name);
      else if (fileType === 'udyam') setUdyamFile(name);
      else if (fileType === 'bank') setBankFile(name);
    }
  };

  const handleClearFile = (fileType: 'pan' | 'aadhaar' | 'udyam' | 'bank') => {
    if (fileType === 'pan') setPanFile(null);
    else if (fileType === 'aadhaar') setAadhaarFile(null);
    else if (fileType === 'udyam') setUdyamFile(null);
    else if (fileType === 'bank') setBankFile(null);
  };

  // Validate Step 1
  const validateStep1 = () => {
    setErrorMsg(null);
    if (!businessName || !ownerName || !mobileNumber || !email || !panNumber || !yearsInBusiness || !loanAmount) {
      setErrorMsg("Please fill in all required fields to proceed.");
      return false;
    }
    const panRegex = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;
    if (!panRegex.test(panNumber.trim().toUpperCase())) {
      setErrorMsg("Invalid PAN Format. Must match standard Indian PAN (e.g. ABCDE1234F).");
      return false;
    }
    return true;
  };

  // Navigate Steps
  const goToNextStep = () => {
    if (currentStep === 1) {
      if (!validateStep1()) return;
    }
    setDirection(1);
    setCurrentStep(prev => prev + 1);
  };

  const goToPrevStep = () => {
    setDirection(-1);
    setCurrentStep(prev => prev - 1);
  };

  // Form submit handler
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);

    // Must connect or upload bank statement
    if (!connectAa && !bankFile) {
      setErrorMsg("Please either connect your Bank Account via Account Aggregator or upload a Bank Statement PDF fallback to proceed.");
      return;
    }

    setSubmitting(true);

    try {
      const payload = {
        business_name: businessName,
        owner_name: ownerName,
        mobile_number: mobileNumber,
        email: email,
        pan_number: panNumber.toUpperCase(),
        // Only send `gstin`/`udyam_number` when the user filled them in — the
        // backend Pydantic model expects `Optional[str]`, which is `undefined`
        // in TS-land, not `null`.
        ...(gstin ? { gstin: gstin.toUpperCase() } : {}),
        ...(udyamNumber ? { udyam_number: udyamNumber } : {}),
        business_type: businessType,
        industry: industry,
        years_in_business: parseInt(yearsInBusiness),
        loan_amount_required: parseFloat(loanAmount),
        loan_purpose: loanPurpose,
        connect_gst: connectGst,
        connect_aa: connectAa,
        connect_upi: connectUpi,
        connect_epfo: connectEpfo,
        ...(panFile ? { upload_pan: panFile } : {}),
        ...(aadhaarFile ? { upload_aadhaar: aadhaarFile } : {}),
        ...(udyamFile ? { upload_udyam: udyamFile } : {}),
        ...(bankFile ? { upload_bank: bankFile } : {}),
      };

      const result = await registerMSME(payload);
      localStorage.setItem('active_business_id', result.business_id);
      queryClient.invalidateQueries({ queryKey: ['business'] });
      queryClient.invalidateQueries({ queryKey: ['portfolio'] });
      setRegisteredId(result.business_id);
      setIsAnalyzing(true);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to submit loan registration. Make sure the backend server is running.");
    } finally {
      setSubmitting(false);
    }
  };

  const connectedCount = [connectGst, connectAa, connectUpi, connectEpfo].filter(Boolean).length;

  return (
    <div className="min-h-screen flex flex-col bg-background font-sans selection:bg-[#008269] selection:text-white">
      <nav className="sticky top-0 z-50 bg-white border-b border-border">
        <div className="max-w-[1440px] mx-auto px-6 lg:px-12 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-[#008269] rounded flex items-center justify-center">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <span className="font-semibold text-lg text-[#008269] tracking-tight">MSME360 CreditPulse</span>
          </div>
          <button 
            onClick={() => navigate('/login')} 
            className="text-sm font-semibold text-text-secondary hover:text-[#008269] transition-colors"
          >
            Back to Sign In
          </button>
        </div>
      </nav>

      <main className="flex-grow flex flex-col items-center bg-[#fafafa]">
        <AnimatePresence mode="wait">
          {!isAnalyzing ? (
            <div className="w-full max-w-4xl px-4 md:px-8 py-10">
              <div className="mb-8">
                <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-white border border-border rounded-full text-xs font-medium text-text-secondary mb-4 shadow-sm">
                  <ShieldCheck className="w-4 h-4 text-success" />
                  IDBI Consent-Driven Lending Framework
                </div>
                <h1 className="text-2xl md:text-3xl font-bold text-text-primary mb-2">Consent-Based Loan Application</h1>
                <p className="text-sm text-text-secondary leading-relaxed">
                  Provide your basic details, connect your accounts via secure digital consent to fetch live data instantly, or upload fallbacks if digital services are unavailable.
                </p>
              </div>

              {/* Stepper Progress Bar */}
              <div className="w-full glass-panel p-5 mb-8 flex items-center justify-between">
                <div className="flex items-center w-full max-w-2xl mx-auto justify-between relative">
                  {/* Background Progress bar line */}
                  <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-border -translate-y-1/2 z-0" />
                  <div 
                    className="absolute top-1/2 left-0 h-0.5 bg-[#008269] -translate-y-1/2 z-0 transition-all duration-300"
                    style={{ width: `${((currentStep - 1) / 2) * 100}%` }}
                  />

                  {/* Step 1 indicator */}
                  <button 
                    type="button"
                    onClick={() => { if (validateStep1()) { setDirection(-1); setCurrentStep(1); } }}
                    className="relative z-10 flex flex-col items-center gap-1 cursor-pointer focus:outline-none"
                  >
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs transition-all duration-300 ${
                      currentStep >= 1 ? 'bg-[#008269] text-white' : 'bg-background-muted text-text-secondary border border-border'
                    }`}>
                      1
                    </div>
                    <span className="text-[10px] font-bold text-text-primary">Business Profile</span>
                  </button>

                  {/* Step 2 indicator */}
                  <button 
                    type="button"
                    onClick={() => { if (validateStep1()) { setDirection(currentStep > 2 ? -1 : 1); setCurrentStep(2); } }}
                    className="relative z-10 flex flex-col items-center gap-1 cursor-pointer focus:outline-none"
                  >
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs transition-all duration-300 ${
                      currentStep >= 2 ? 'bg-[#008269] text-white' : 'bg-background-muted text-text-secondary border border-border'
                    }`}>
                      2
                    </div>
                    <span className="text-[10px] font-bold text-text-primary">Digital Consents</span>
                  </button>

                  {/* Step 3 indicator */}
                  <button 
                    type="button"
                    onClick={() => { if (validateStep1()) { setDirection(1); setCurrentStep(3); } }}
                    className="relative z-10 flex flex-col items-center gap-1 cursor-pointer focus:outline-none"
                  >
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs transition-all duration-300 ${
                      currentStep >= 3 ? 'bg-[#008269] text-white' : 'bg-background-muted text-text-secondary border border-border'
                    }`}>
                      3
                    </div>
                    <span className="text-[10px] font-bold text-text-primary">Fallback Uploads</span>
                  </button>
                </div>
              </div>

              {errorMsg && (
                <div className="mb-6 p-4 bg-error/10 border border-error/20 text-error rounded-card text-sm font-semibold flex items-center gap-3">
                  <AlertCircle className="w-5 h-5 shrink-0" />
                  <span>{errorMsg}</span>
                </div>
              )}

              {/* Animated Switcher Area */}
              <div className="relative overflow-hidden min-h-[400px]">
                <AnimatePresence initial={false} custom={direction} mode="wait">
                  {currentStep === 1 && (
                    <motion.div
                      key="step1"
                      custom={direction}
                      variants={slideVariants}
                      initial="enter"
                      animate="center"
                      exit="exit"
                      className="bg-white border border-border rounded-card shadow-card p-6 md:p-8 space-y-6"
                    >
                      <div className="flex items-center gap-2 mb-2 border-b border-border pb-4">
                        <div className="w-8 h-8 rounded bg-[#008269]/10 text-[#008269] flex items-center justify-center font-bold">1</div>
                        <div>
                          <h3 className="text-base font-bold text-text-primary">Basic Business Information</h3>
                          <p className="text-xs text-text-secondary">Please enter your business registration & loan specifications.</p>
                        </div>
                       </div>

                      {/* Document Intelligence OCR Widget */}
                      <div className="bg-[#008269]/5 border border-[#008269]/20 rounded-lg p-4 mb-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="text-xs font-bold text-[#008269] uppercase tracking-wider flex items-center gap-1.5">
                            <BrainCircuit className="w-4 h-4" /> AI Document Intelligence
                          </h4>
                          {ocrSource && (
                            <span className="text-[9px] font-semibold text-[#008269]/70 bg-[#008269]/10 px-2 py-0.5 rounded-full flex items-center gap-1">
                              <Sparkles className="w-3 h-3" /> {ocrSource}
                            </span>
                          )}
                        </div>
                        <p className="text-[11px] text-text-secondary leading-relaxed mb-3">
                          Upload a <strong>bank statement image</strong> (PNG/JPEG) for Gemini Vision extraction, or a <strong>CSV bank statement</strong> for instant parsing. Fields will auto-populate below.
                        </p>
                        
                        {isOcrLoading ? (
                          <div className="flex flex-col items-center justify-center py-6 bg-white border border-[#008269]/20 border-dashed rounded-lg">
                            <div className="relative mb-3">
                              <Loader2 className="w-7 h-7 text-[#008269] animate-spin" />
                              <div className="absolute inset-0 w-7 h-7 rounded-full border-2 border-[#008269]/20 animate-ping" />
                            </div>
                            <span className="text-[11px] font-semibold text-text-primary animate-pulse">{ocrProgressText}</span>
                            {ocrFileName && <span className="text-[9px] text-text-secondary mt-1">Processing: {ocrFileName}</span>}
                          </div>
                        ) : ocrSuccess ? (
                          <div className="space-y-2">
                            <div className="p-3 bg-success/10 border border-success/25 rounded-lg text-success text-[11px] font-semibold flex items-center justify-between">
                              <div className="flex items-center gap-1.5">
                                <CheckCircle2 className="w-4 h-4" />
                                <span>{ocrSuccess}</span>
                              </div>
                              <button
                                type="button"
                                onClick={() => {
                                  setOcrSuccess(null);
                                  setOcrSource(null);
                                  setOcrExtracted(null);
                                  setOcrFileName(null);
                                }}
                                className="text-[10px] text-text-secondary hover:underline cursor-pointer flex items-center gap-1"
                              >
                                <X className="w-3 h-3" /> Clear & Re-upload
                              </button>
                            </div>
                            
                            {/* Extracted Financial Summary (shown for CSV) */}
                            {ocrExtracted && (ocrExtracted.total_credits || ocrExtracted.transaction_count) && (
                              <div className="bg-white border border-border rounded-lg p-3">
                                <div className="flex items-center gap-1.5 mb-2">
                                  <Info className="w-3.5 h-3.5 text-[#008269]" />
                                  <span className="text-[10px] font-bold text-text-primary uppercase tracking-wider">Extracted Financial Summary</span>
                                </div>
                                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                                  {ocrExtracted.total_credits != null && ocrExtracted.total_credits > 0 && (
                                    <div className="bg-success/5 border border-success/15 rounded px-2.5 py-1.5">
                                      <p className="text-[8px] font-bold text-success uppercase">Total Credits</p>
                                      <p className="text-xs font-bold text-text-primary">{formatINR(ocrExtracted.total_credits)}</p>
                                    </div>
                                  )}
                                  {ocrExtracted.total_debits != null && ocrExtracted.total_debits > 0 && (
                                    <div className="bg-error/5 border border-error/15 rounded px-2.5 py-1.5">
                                      <p className="text-[8px] font-bold text-error uppercase">Total Debits</p>
                                      <p className="text-xs font-bold text-text-primary">{formatINR(ocrExtracted.total_debits)}</p>
                                    </div>
                                  )}
                                  {ocrExtracted.average_balance != null && ocrExtracted.average_balance > 0 && (
                                    <div className="bg-[#008269]/5 border border-[#008269]/15 rounded px-2.5 py-1.5">
                                      <p className="text-[8px] font-bold text-[#008269] uppercase">Avg Balance</p>
                                      <p className="text-xs font-bold text-text-primary">{formatINR(ocrExtracted.average_balance)}</p>
                                    </div>
                                  )}
                                  {ocrExtracted.transaction_count != null && ocrExtracted.transaction_count > 0 && (
                                    <div className="bg-primary/5 border border-primary/15 rounded px-2.5 py-1.5">
                                      <p className="text-[8px] font-bold text-primary uppercase">Transactions</p>
                                      <p className="text-xs font-bold text-text-primary">{ocrExtracted.transaction_count}</p>
                                    </div>
                                  )}
                                </div>
                                {ocrExtracted.statement_period_start && ocrExtracted.statement_period_end && (
                                  <p className="text-[9px] text-text-secondary mt-2">
                                    Statement Period: <strong>{ocrExtracted.statement_period_start}</strong> to <strong>{ocrExtracted.statement_period_end}</strong>
                                    {ocrExtracted.industry_hint && <> &middot; Industry: <strong>{ocrExtracted.industry_hint}</strong></>}
                                  </p>
                                )}
                                {ocrExtracted._mock && (
                                  <p className="text-[9px] text-amber-600 mt-1.5 flex items-center gap-1">
                                    <AlertCircle className="w-3 h-3" /> Demo mode — set GEMINI_API_KEY for real vision extraction
                                  </p>
                                )}
                              </div>
                            )}
                          </div>
                        ) : (
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                            {/* Image upload zone */}
                            <div className="border border-border border-dashed rounded-lg p-4 flex flex-col items-center justify-center relative hover:bg-white hover:border-[#008269]/40 transition-all bg-white min-h-[100px] group cursor-pointer">
                              <Camera className="w-5 h-5 text-text-secondary mb-2 group-hover:text-[#008269] transition-colors" />
                              <p className="text-[11px] font-semibold text-text-primary group-hover:text-[#008269] transition-colors">Paper Statement Photo</p>
                              <p className="text-[9px] text-text-secondary mt-0.5">PNG or JPEG up to 5MB</p>
                              <input 
                                type="file" 
                                accept="image/png,image/jpeg,image/jpg,image/webp"
                                onChange={handleOcrFileSelect}
                                className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
                              />
                            </div>
                            {/* CSV upload zone */}
                            <div className="border border-border border-dashed rounded-lg p-4 flex flex-col items-center justify-center relative hover:bg-white hover:border-[#008269]/40 transition-all bg-white min-h-[100px] group cursor-pointer">
                              <FileSpreadsheet className="w-5 h-5 text-text-secondary mb-2 group-hover:text-[#008269] transition-colors" />
                              <p className="text-[11px] font-semibold text-text-primary group-hover:text-[#008269] transition-colors">CSV Bank Statement</p>
                              <p className="text-[9px] text-text-secondary mt-0.5">Exported from net banking</p>
                              <input 
                                type="file" 
                                accept=".csv,text/csv"
                                onChange={handleOcrFileSelect}
                                className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
                              />
                            </div>
                          </div>
                        )}
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                        <div>
                          <label className="block text-xs font-bold text-text-primary uppercase tracking-wider mb-2">Business Name *</label>
                          <input 
                            type="text" 
                            placeholder="e.g. Surat Silk Sarees"
                            value={businessName}
                            onChange={(e) => setBusinessName(e.target.value)}
                            className="w-full px-4 py-2.5 border border-border bg-white rounded text-xs focus:outline-none focus:border-[#008269]"
                            required
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-bold text-text-primary uppercase tracking-wider mb-2">Owner Name *</label>
                          <input 
                            type="text" 
                            placeholder="e.g. Ayesha Mehta"
                            value={ownerName}
                            onChange={(e) => setOwnerName(e.target.value)}
                            className="w-full px-4 py-2.5 border border-border bg-white rounded text-xs focus:outline-none focus:border-[#008269]"
                            required
                          />
                        </div>

                        <div>
                          <label className="block text-xs font-bold text-text-primary uppercase tracking-wider mb-2">Mobile Number *</label>
                          <input 
                            type="tel" 
                            placeholder="e.g. 9876543210"
                            value={mobileNumber}
                            onChange={(e) => setMobileNumber(e.target.value)}
                            className="w-full px-4 py-2.5 border border-border bg-white rounded text-xs focus:outline-none focus:border-[#008269]"
                            required
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-bold text-text-primary uppercase tracking-wider mb-2">Email Address *</label>
                          <input 
                            type="email" 
                            placeholder="e.g. contact@suratsilks.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="w-full px-4 py-2.5 border border-border bg-white rounded text-xs focus:outline-none focus:border-[#008269]"
                            required
                          />
                        </div>

                        <div>
                          <label className="block text-xs font-bold text-text-primary uppercase tracking-wider mb-2">PAN Number (Business/Proprietor) *</label>
                          <input 
                            type="text" 
                            placeholder="e.g. ABCDE1234F"
                            value={panNumber}
                            onChange={(e) => setPanNumber(e.target.value.toUpperCase())}
                            className="w-full px-4 py-2.5 border border-border bg-white rounded text-xs focus:outline-none focus:border-[#008269] uppercase font-semibold"
                            required
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-bold text-text-primary uppercase tracking-wider mb-2">GSTIN (GST Identification Number)</label>
                          <input 
                            type="text" 
                            placeholder="Optional (e.g. 27ABCDE1234F1Z5)"
                            value={gstin}
                            onChange={(e) => setGstin(e.target.value.toUpperCase())}
                            className="w-full px-4 py-2.5 border border-border bg-white rounded text-xs focus:outline-none focus:border-[#008269] uppercase"
                          />
                        </div>

                        <div>
                          <label className="block text-xs font-bold text-text-primary uppercase tracking-wider mb-2">Udyam Registration Number</label>
                          <input 
                            type="text" 
                            placeholder="Optional (e.g. UDYAM-MH-01-1234567)"
                            value={udyamNumber}
                            onChange={(e) => setUdyamNumber(e.target.value)}
                            className="w-full px-4 py-2.5 border border-border bg-white rounded text-xs focus:outline-none focus:border-[#008269]"
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-bold text-text-primary uppercase tracking-wider mb-2">Business Constitution *</label>
                          <select 
                            value={businessType}
                            onChange={(e) => setBusinessType(e.target.value)}
                            className="w-full px-4 py-2.5 border border-border bg-white rounded text-xs focus:outline-none focus:border-[#008269] text-text-primary font-medium"
                          >
                            <option value="Sole Proprietor">Sole Proprietor</option>
                            <option value="Partnership">Partnership</option>
                            <option value="Pvt Ltd">Pvt Ltd Company</option>
                            <option value="LLP">Limited Liability Partnership</option>
                          </select>
                        </div>

                        <div>
                          <label className="block text-xs font-bold text-text-primary uppercase tracking-wider mb-2">Industry Sector *</label>
                          <select 
                            value={industry}
                            onChange={(e) => setIndustry(e.target.value)}
                            className="w-full px-4 py-2.5 border border-border bg-white rounded text-xs focus:outline-none focus:border-[#008269] text-text-primary font-medium"
                          >
                            <option value="Manufacturing">Manufacturing</option>
                            <option value="Retail">Retail Trade</option>
                            <option value="Wholesale">Wholesale Trade</option>
                            <option value="Services">Services Sector</option>
                            <option value="Logistics">Logistics & Transport</option>
                            <option value="Others">Others</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-xs font-bold text-text-primary uppercase tracking-wider mb-2">Years in Business *</label>
                          <input 
                            type="number" 
                            min="1"
                            placeholder="e.g. 5"
                            value={yearsInBusiness}
                            onChange={(e) => setYearsInBusiness(e.target.value)}
                            className="w-full px-4 py-2.5 border border-border bg-white rounded text-xs focus:outline-none focus:border-[#008269]"
                            required
                          />
                        </div>

                        <div>
                          <label className="block text-xs font-bold text-text-primary uppercase tracking-wider mb-2">Required Loan Amount (INR) *</label>
                          <input 
                            type="number" 
                            placeholder="e.g. 1500000"
                            value={loanAmount}
                            onChange={(e) => setLoanAmount(e.target.value)}
                            className="w-full px-4 py-2.5 border border-border bg-white rounded text-xs focus:outline-none focus:border-[#008269] font-semibold"
                            required
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-bold text-text-primary uppercase tracking-wider mb-2">Loan Purpose *</label>
                          <select 
                            value={loanPurpose}
                            onChange={(e) => setLoanPurpose(e.target.value)}
                            className="w-full px-4 py-2.5 border border-border bg-white rounded text-xs focus:outline-none focus:border-[#008269] text-text-primary font-medium"
                          >
                            <option value="Working Capital">Working Capital</option>
                            <option value="Machinery Acquisition">Machinery / Equipment Purchase</option>
                            <option value="Business Expansion">Business Expansion</option>
                            <option value="Inventory Stocking">Inventory Purchase</option>
                            <option value="Debt Refinancing">Debt Consolidation</option>
                          </select>
                        </div>
                      </div>

                      <div className="flex justify-end pt-4 border-t border-border mt-6">
                        <button 
                          type="button" 
                          onClick={goToNextStep}
                          className="bg-[#008269] hover:bg-[#005443] text-white px-6 py-2.5 rounded font-bold flex items-center gap-2 transition-colors cursor-pointer"
                        >
                          Continue to Consents
                          <ArrowRight className="w-4 h-4" />
                        </button>
                      </div>
                    </motion.div>
                  )}

                  {currentStep === 2 && (
                    <motion.div
                      key="step2"
                      custom={direction}
                      variants={slideVariants}
                      initial="enter"
                      animate="center"
                      exit="exit"
                      className="bg-white border border-border rounded-card shadow-card p-6 md:p-8 space-y-6"
                    >
                      <div className="flex items-center gap-2 mb-2 border-b border-border pb-4">
                        <div className="w-8 h-8 rounded bg-[#008269]/10 text-[#008269] flex items-center justify-center font-bold">2</div>
                        <div>
                          <h3 className="text-base font-bold text-text-primary">Digital Consent Pipelines</h3>
                          <p className="text-xs text-text-secondary">Real-time alternate data connection pipelines.</p>
                        </div>
                      </div>

                      {/* Sub-step breadcrumbs flow */}
                      <div className="flex justify-between items-center text-[10px] text-text-secondary bg-[#008269]/5 border border-[#008269]/15 p-3 rounded font-semibold">
                        <span>Consent Progress:</span>
                        <div className="flex items-center gap-1.5 uppercase tracking-wider">
                          <span className={consentSubStep >= 1 ? "text-[#008269] font-bold" : ""}>1. GST</span>
                          <span>➔</span>
                          <span className={consentSubStep >= 2 ? "text-[#008269] font-bold" : ""}>2. Bank (AA)</span>
                          <span>➔</span>
                          <span className={consentSubStep >= 3 ? "text-[#008269] font-bold" : ""}>3. UPI</span>
                          <span>➔</span>
                          <span className={consentSubStep >= 4 ? "text-[#008269] font-bold" : ""}>4. EPFO</span>
                        </div>
                      </div>

                      <div className="space-y-4">
                        
                        {/* GST Returns Pipeline */}
                        {consentSubStep >= 1 && (
                          <motion.div 
                            initial={{ opacity: 0, y: 15 }}
                            animate={{ opacity: 1, y: 0 }}
                            className={`border rounded p-4 flex flex-col justify-between transition-all bg-white shadow-xs ${
                              consentSubStep === 1 ? 'border-[#008269] ring-2 ring-[#008269]/10' : 'border-border/60 bg-[#fafafa]/80'
                            }`}
                          >
                            <div className="flex items-start gap-3">
                              <div className={`p-2 rounded ${consentSubStep === 1 ? 'bg-[#008269]/10 text-[#008269]' : 'bg-success/10 text-success'}`}>
                                <FileText className="w-5 h-5" />
                              </div>
                              <div className="flex-1">
                                <h4 className="text-xs font-bold text-text-primary">GST Returns Pipeline</h4>
                                <p className="text-[10px] text-text-secondary leading-relaxed mt-0.5">Fetches turnover, tax filing timelines and compliance history from GSTN.</p>
                              </div>
                            </div>
                            <div className="mt-4 border-t border-border/40 pt-3 flex justify-between items-center">
                              <span className="text-[10px] font-semibold text-text-secondary">
                                {connectingGst ? (
                                  <span className="flex items-center gap-1.5 text-primary"><Loader2 className="w-3.5 h-3.5 animate-spin" /> Connecting to GSTN registry...</span>
                                ) : connectGst ? (
                                  <span className="flex items-center gap-1.5 text-success font-bold"><Check className="w-3.5 h-3.5" /> GSTN Connected successfully</span>
                                ) : (
                                  "Status: Disconnected"
                                )}
                              </span>
                            </div>
                          </motion.div>
                        )}

                        {/* Account Aggregator (Bank Data) */}
                        {consentSubStep >= 2 && (
                          <motion.div 
                            initial={{ opacity: 0, y: 15 }}
                            animate={{ opacity: 1, y: 0 }}
                            className={`border rounded p-4 flex flex-col justify-between transition-all bg-white shadow-xs ${
                              consentSubStep === 2 ? 'border-[#008269] ring-2 ring-[#008269]/10' : 'border-border/60 bg-[#fafafa]/80'
                            }`}
                          >
                            <div className="flex items-start gap-3">
                              <div className={`p-2 rounded ${consentSubStep === 2 ? 'bg-[#008269]/10 text-[#008269]' : 'bg-success/10 text-success'}`}>
                                <Landmark className="w-5 h-5" />
                              </div>
                              <div className="flex-1">
                                <h4 className="text-xs font-bold text-text-primary">Account Aggregator (Bank Statement)</h4>
                                <p className="text-[10px] text-text-secondary leading-relaxed mt-0.5">Secure, consent-driven bank statements, month-end balances, and EMIs.</p>
                              </div>
                            </div>
                            <div className="mt-4 border-t border-border/40 pt-3 flex justify-between items-center">
                              <span className="text-[10px] font-semibold text-text-secondary">
                                {connectingAa ? (
                                  <span className="flex items-center gap-1.5 text-primary"><Loader2 className="w-3.5 h-3.5 animate-spin" /> Fetching bank records via secure consent...</span>
                                ) : connectAa ? (
                                  <span className="flex items-center gap-1.5 text-success font-bold"><Check className="w-3.5 h-3.5" /> Account Aggregator Linked successfully</span>
                                ) : (
                                  "Status: Disconnected"
                                )}
                              </span>
                            </div>
                          </motion.div>
                        )}

                        {/* UPI Transactions Velocity */}
                        {consentSubStep >= 3 && (
                          <motion.div 
                            initial={{ opacity: 0, y: 15 }}
                            animate={{ opacity: 1, y: 0 }}
                            className={`border rounded p-4 flex flex-col justify-between transition-all bg-white shadow-xs ${
                              consentSubStep === 3 ? 'border-[#008269] ring-2 ring-[#008269]/10' : 'border-border/60 bg-[#fafafa]/80'
                            }`}
                          >
                            <div className="flex items-start gap-3">
                              <div className={`p-2 rounded ${consentSubStep === 3 ? 'bg-[#008269]/10 text-[#008269]' : 'bg-success/10 text-success'}`}>
                                <Smartphone className="w-5 h-5" />
                              </div>
                              <div className="flex-1">
                                <h4 className="text-xs font-bold text-text-primary">UPI Transactions Velocity</h4>
                                <p className="text-[10px] text-text-secondary leading-relaxed mt-0.5">QR payments volume, merchant transaction frequency, and digital collection ratios.</p>
                              </div>
                            </div>
                            <div className="mt-4 border-t border-border/40 pt-3 flex justify-between items-center">
                              <span className="text-[10px] font-semibold text-text-secondary">
                                {connectingUpi ? (
                                  <span className="flex items-center gap-1.5 text-primary"><Loader2 className="w-3.5 h-3.5 animate-spin" /> Calculating transaction velocity...</span>
                                ) : connectUpi ? (
                                  <span className="flex items-center gap-1.5 text-success font-bold"><Check className="w-3.5 h-3.5" /> UPI Collection terminal active</span>
                                ) : (
                                  "Status: Disconnected"
                                )}
                              </span>
                            </div>
                          </motion.div>
                        )}

                        {/* EPFO Payroll Deposits */}
                        {consentSubStep >= 4 && (
                          <motion.div 
                            initial={{ opacity: 0, y: 15 }}
                            animate={{ opacity: 1, y: 0 }}
                            className={`border rounded p-4 flex flex-col justify-between transition-all bg-white shadow-xs ${
                              consentSubStep === 4 ? 'border-[#008269] ring-2 ring-[#008269]/10' : 'border-border/60 bg-[#fafafa]/80'
                            }`}
                          >
                            <div className="flex items-start gap-3">
                              <div className={`p-2 rounded ${consentSubStep === 4 ? 'bg-[#008269]/10 text-[#008269]' : 'bg-success/10 text-success'}`}>
                                <Briefcase className="w-5 h-5" />
                              </div>
                              <div className="flex-1">
                                <h4 className="text-xs font-bold text-text-primary">EPFO Payroll Deposits</h4>
                                <p className="text-[10px] text-text-secondary leading-relaxed mt-0.5">Fetches monthly employee count, payroll deposits, and company vintage stability.</p>
                              </div>
                            </div>
                            <div className="mt-4 border-t border-border/40 pt-3 flex justify-between items-center">
                              <span className="text-[10px] font-semibold text-text-secondary">
                                {connectingEpfo ? (
                                  <span className="flex items-center gap-1.5 text-primary"><Loader2 className="w-3.5 h-3.5 animate-spin" /> Verifying EPFO payroll vintage...</span>
                                ) : connectEpfo ? (
                                  <span className="flex items-center gap-1.5 text-success font-bold"><Check className="w-3.5 h-3.5" /> EPFO Payroll synced successfully</span>
                                ) : (
                                  "Status: Disconnected"
                                )}
                              </span>
                            </div>
                          </motion.div>
                        )}

                      </div>

                      <div className="flex justify-between pt-4 border-t border-border mt-6">
                        <button 
                          type="button" 
                          onClick={handlePrevConsentSubStep}
                          className="bg-white border border-border hover:bg-background-muted text-text-primary px-6 py-2.5 rounded font-bold flex items-center gap-2 transition-colors cursor-pointer"
                        >
                          <ArrowLeft className="w-4 h-4" />
                          Back
                        </button>
                        
                        <button 
                          type="button" 
                          onClick={handleNextConsentSubStep}
                          disabled={
                            (consentSubStep === 1 && (connectingGst || !connectGst)) ||
                            (consentSubStep === 2 && (connectingAa || !connectAa)) ||
                            (consentSubStep === 3 && (connectingUpi || !connectUpi)) ||
                            (consentSubStep === 4 && (connectingEpfo || !connectEpfo))
                          }
                          className="bg-[#008269] hover:bg-[#005443] disabled:opacity-50 disabled:cursor-not-allowed text-white px-6 py-2.5 rounded font-bold flex items-center gap-2 transition-colors cursor-pointer"
                        >
                          {consentSubStep === 4 ? "Continue to Uploads" : "Connect Next Pipeline"}
                          <ArrowRight className="w-4 h-4" />
                        </button>
                      </div>
                    </motion.div>
                  )}

                  {currentStep === 3 && (
                    <motion.div
                      key="step3"
                      custom={direction}
                      variants={slideVariants}
                      initial="enter"
                      animate="center"
                      exit="exit"
                      className="bg-white border border-border rounded-card shadow-card p-6 md:p-8 space-y-6"
                    >
                      <div className="flex items-center gap-2 mb-2 border-b border-border pb-4">
                        <div className="w-8 h-8 rounded bg-[#008269]/10 text-[#008269] flex items-center justify-center font-bold">3</div>
                        <div>
                          <h3 className="text-base font-bold text-text-primary">Optional Uploads (Fallback)</h3>
                          <p className="text-xs text-text-secondary">Only upload if digital data connections above are unavailable.</p>
                        </div>
                      </div>

                      <p className="text-xs text-text-secondary leading-relaxed">
                        If you could not connect your accounts via consent pipelines in Step 2, please upload the fallback physical documents below to complete underwriting validation.
                      </p>

                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        {/* PAN Card upload */}
                        <div className="border border-border border-dashed rounded p-4 flex flex-col items-center justify-center relative hover:bg-background-muted/20 transition-all bg-white min-h-[120px]">
                          {panFile ? (
                            <div className="text-center w-full">
                              <CheckCircle2 className="w-8 h-8 text-success mx-auto mb-2" />
                              <p className="text-xs font-semibold text-text-primary truncate px-2">{panFile}</p>
                              <button 
                                type="button" 
                                onClick={() => handleClearFile('pan')}
                                className="mt-2 text-[10px] text-error hover:underline cursor-pointer"
                              >
                                Remove
                              </button>
                            </div>
                          ) : (
                            <>
                              <Upload className="w-6 h-6 text-text-secondary mb-2" />
                              <p className="text-[11px] font-semibold text-text-primary">Upload PAN Card</p>
                              <p className="text-[9px] text-text-secondary mt-0.5">PDF, PNG or JPG up to 5MB</p>
                              <input 
                                type="file" 
                                accept=".pdf,image/*"
                                onChange={(e) => handleMockUpload(e, 'pan')}
                                className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
                              />
                            </>
                          )}
                        </div>

                        {/* Aadhaar upload */}
                        <div className="border border-border border-dashed rounded p-4 flex flex-col items-center justify-center relative hover:bg-background-muted/20 transition-all bg-white min-h-[120px]">
                          {aadhaarFile ? (
                            <div className="text-center w-full">
                              <CheckCircle2 className="w-8 h-8 text-success mx-auto mb-2" />
                              <p className="text-xs font-semibold text-text-primary truncate px-2">{aadhaarFile}</p>
                              <button 
                                type="button" 
                                onClick={() => handleClearFile('aadhaar')}
                                className="mt-2 text-[10px] text-error hover:underline cursor-pointer"
                              >
                                Remove
                              </button>
                            </div>
                          ) : (
                            <>
                              <Upload className="w-6 h-6 text-text-secondary mb-2" />
                              <p className="text-[11px] font-semibold text-text-primary">Upload Aadhaar Card</p>
                              <p className="text-[9px] text-text-secondary mt-0.5">PDF or image format</p>
                              <input 
                                type="file" 
                                accept=".pdf,image/*"
                                onChange={(e) => handleMockUpload(e, 'aadhaar')}
                                className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
                              />
                            </>
                          )}
                        </div>

                        {/* Udyam Certificate upload */}
                        <div className="border border-border border-dashed rounded p-4 flex flex-col items-center justify-center relative hover:bg-background-muted/20 transition-all bg-white min-h-[120px]">
                          {udyamFile ? (
                            <div className="text-center w-full">
                              <CheckCircle2 className="w-8 h-8 text-success mx-auto mb-2" />
                              <p className="text-xs font-semibold text-text-primary truncate px-2">{udyamFile}</p>
                              <button 
                                type="button" 
                                onClick={() => handleClearFile('udyam')}
                                className="mt-2 text-[10px] text-error hover:underline cursor-pointer"
                              >
                                Remove
                              </button>
                            </div>
                          ) : (
                            <>
                              <Upload className="w-6 h-6 text-text-secondary mb-2" />
                              <p className="text-[11px] font-semibold text-text-primary">Udyam Registration Certificate</p>
                              <p className="text-[9px] text-text-secondary mt-0.5">MSME verification document</p>
                              <input 
                                type="file" 
                                accept=".pdf,image/*"
                                onChange={(e) => handleMockUpload(e, 'udyam')}
                                className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
                              />
                            </>
                          )}
                        </div>

                        {/* Bank Statement upload */}
                        <div className="border border-border border-dashed rounded p-4 flex flex-col items-center justify-center relative hover:bg-background-muted/20 transition-all bg-white min-h-[120px]">
                          {bankFile ? (
                            <div className="text-center w-full">
                              <CheckCircle2 className="w-8 h-8 text-success mx-auto mb-2" />
                              <p className="text-xs font-semibold text-text-primary truncate px-2">{bankFile}</p>
                              <button 
                                type="button" 
                                onClick={() => handleClearFile('bank')}
                                className="mt-2 text-[10px] text-error hover:underline cursor-pointer"
                              >
                                Remove
                              </button>
                            </div>
                          ) : (
                            <>
                              <Upload className="w-6 h-6 text-text-secondary mb-2" />
                              <p className="text-[11px] font-semibold text-text-primary">Bank Statements (Fallback)</p>
                              <p className="text-[9px] text-text-secondary mt-0.5">PDF or CSV from last 6 months</p>
                              <input 
                                type="file" 
                                accept=".pdf,.csv"
                                onChange={(e) => handleMockUpload(e, 'bank')}
                                className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
                              />
                            </>
                          )}
                        </div>
                      </div>

                      <div className="bg-[#fafafa] border border-border p-5 rounded flex flex-col sm:flex-row items-center justify-between gap-4 mt-6">
                        <div className="text-center sm:text-left">
                          <span className="text-xs font-bold text-text-primary block">{connectedCount} Source(s) Connected</span>
                          <span className="text-[10px] text-text-secondary mt-0.5 block">
                            {!connectAa && !bankFile 
                              ? "⚠ Please connect your bank account (Step 2) or upload a Bank Statement PDF above" 
                              : "Verified: Required financial data source is available."}
                          </span>
                        </div>
                        <div className="flex gap-3 w-full sm:w-auto">
                          <button 
                            type="button" 
                            onClick={goToPrevStep}
                            className="bg-white border border-border hover:bg-background-muted text-text-primary px-5 py-2.5 rounded font-bold flex items-center justify-center gap-2 transition-colors cursor-pointer flex-1 sm:flex-initial"
                          >
                            <ArrowLeft className="w-4 h-4" />
                            Back
                          </button>
                          <button 
                            onClick={handleSubmit}
                            disabled={submitting || (!connectAa && !bankFile)}
                            className="bg-[#008269] hover:bg-[#005443] text-white px-6 py-2.5 rounded font-bold flex items-center justify-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer flex-1 sm:flex-initial"
                          >
                            {submitting ? (
                              <>
                                <Loader2 className="w-4 h-4 animate-spin" />
                                Analyzing...
                              </>
                            ) : (
                              <>
                                Analyze My Business
                                <ArrowRight className="w-4 h-4" />
                              </>
                            )}
                          </button>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          ) : (
            <motion.div 
              key="loader-view"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="w-full flex-grow flex items-center justify-center py-10"
            >
              <AnalysisWorkflow businessId={registeredId} />
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
