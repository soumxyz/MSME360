import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { 
  BarChart3, 
  Link as LinkIcon, 
  Activity, 
  Landmark, 
  ChevronRight,
  ArrowRight,
  Building2,
  Database,
  BrainCircuit,
  FileCheck,
  FileText
} from 'lucide-react';

const FadeIn = ({ children, delay = 0 }: { children: React.ReactNode, delay?: number }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true, margin: "-50px" }}
    transition={{ duration: 0.5, delay }}
  >
    {children}
  </motion.div>
);

const Navbar = () => (
  <nav className="sticky top-0 z-50 bg-white border-b border-border">
    <div className="max-w-[1440px] mx-auto px-6 lg:px-12 h-16 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 bg-primary rounded flex items-center justify-center">
          <Activity className="w-5 h-5 text-white" />
        </div>
        <span className="font-semibold text-lg text-primary tracking-tight">CreditPulse AI</span>
      </div>
      <div className="hidden md:flex items-center gap-8 text-sm font-medium text-text-secondary">
        <a href="#top" className="hover:text-primary transition-colors">Home</a>
        <a href="#features" className="hover:text-primary transition-colors">Features</a>
        <a href="#workflow" className="hover:text-primary transition-colors">How It Works</a>
      </div>
      <div className="flex items-center gap-4 text-sm font-medium">
        <Link to="/login?role=officer" className="text-text-primary hover:text-primary transition-colors">Officer Login</Link>
        <Link to="/login?role=customer" className="bg-primary hover:bg-primary-hover text-white px-4 py-2 rounded transition-colors">
          Open Account
        </Link>
      </div>
    </div>
  </nav>
);

const Hero = () => (
  <section className="bg-background-muted py-24 border-b border-border">
    <div className="max-w-[1440px] mx-auto px-6 lg:px-12">
      <div className="max-w-3xl">
        <FadeIn>
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-white border border-border rounded-full text-xs font-medium text-text-secondary mb-6 shadow-sm">
            <span className="w-2 h-2 rounded-full bg-secondary"></span>
            Enterprise Grade AI Analysis
          </div>
          <h1 className="text-4xl md:text-5xl font-semibold text-text-primary leading-tight mb-6">
            AI Powered Financial Health Assessment for MSMEs
          </h1>
          <p className="text-lg text-text-secondary mb-10 leading-relaxed max-w-2xl">
            Leverage institutional-grade artificial intelligence to analyze your business's financial health, integrate alternate data sources, and receive intelligent loan recommendations tailored to your operational metrics.
          </p>
          <div className="flex flex-wrap items-center gap-4">
            <Link to="/login?role=customer" className="bg-primary hover:bg-primary-hover text-white px-6 py-3 rounded font-medium flex items-center gap-2 transition-colors">
              Start Assessment <ArrowRight className="w-4 h-4" />
            </Link>
            <button className="bg-white border border-border hover:bg-background text-text-primary px-6 py-3 rounded font-medium transition-colors">
              Learn More
            </button>
          </div>
        </FadeIn>
      </div>
    </div>
  </section>
);

const Features = () => {
  // Map icons manually to avoid missing imports
  const activeFeatures = [
    { icon: <BrainCircuit className="w-6 h-6 text-[#008269]" />, title: "AI Financial Health Assessment", description: "Analyzes GST, UPI, Account Aggregator, and EPFO pipelines for alternate credit metrics." },
    { icon: <Building2 className="w-6 h-6 text-[#008269]" />, title: "AI MSME Due Diligence", description: "Verifies entity registrations, tax statuses, and highlights transaction risk alerts." },
    { icon: <Building2 className="w-6 h-6 text-[#008269]" />, title: "KYC & KYB Verification", description: "Seamless, real-time registry checks for PAN, GSTIN, Udyam MSME, and Aadhaar OTP." },
    { icon: <BrainCircuit className="w-6 h-6 text-[#008269]" />, title: "Fraud & Risk Detection", description: "Scans bank statement ledgers for circular flows, balance spikes, and repayment delay risks." },
    { icon: <Activity className="w-6 h-6 text-[#008269]" />, title: "RBI Policy Compliance", description: "Validates internal lending guidelines, document checklists, and MSME sector eligibility." },
    { icon: <FileCheck className="w-6 h-6 text-[#008269]" />, title: "AI Loan Origination", description: "Automates the pre-screening flow from intake checks to underwriter decision approvals." },
    { icon: <BrainCircuit className="w-6 h-6 text-[#008269]" />, title: "AI Credit Copilot", description: "Interactive grounded assistant to explain ratings and suggest underwriting recommendations." },
    { icon: <FileText className="w-6 h-6 text-[#008269]" />, title: "Financial Health Card", description: "Renders multi-dimensional credit grades and explainable attributions in one view." },
    { icon: <Activity className="w-6 h-6 text-[#008269]" />, title: "What-if Loan Simulator", description: "Allows credit officers to dynamically adjust exposure limits and model EMI impact instantly." },
    { icon: <FileText className="w-6 h-6 text-[#008269]" />, title: "AI Credit Memo Generator", description: "One-click drafts of executive rationale credit summaries ready for manager sign-off." }
  ];

  return (
    <section id="features" className="py-24 bg-white border-b border-border">
      <div className="max-w-[1440px] mx-auto px-6 lg:px-12">
        <FadeIn>
          <h2 className="text-3xl font-semibold text-text-primary mb-12">Core Capabilities</h2>
        </FadeIn>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
          {activeFeatures.map((feature, index) => (
            <FadeIn key={index} delay={index * 0.05}>
              <div className="bg-background-card border border-border p-6 rounded-card shadow-card h-full flex flex-col hover:border-[#008269]/40 transition-colors">
                <div className="w-12 h-12 rounded bg-background-muted flex items-center justify-center mb-6">
                  {feature.icon}
                </div>
                <h3 className="text-sm font-semibold text-text-primary mb-3">{feature.title}</h3>
                <p className="text-xs text-text-secondary leading-relaxed flex-grow">
                  {feature.description}
                </p>
              </div>
            </FadeIn>
          ))}
        </div>
      </div>
    </section>
  );
};

const Workflow = () => {
  const steps = [
    { icon: <Building2 className="w-5 h-5 text-text-secondary" />, title: "Register Business" },
    { icon: <Database className="w-5 h-5 text-text-secondary" />, title: "Connect Data" },
    { icon: <BrainCircuit className="w-5 h-5 text-text-secondary" />, title: "AI Analysis" },
    { icon: <BarChart3 className="w-5 h-5 text-text-secondary" />, title: "Health Score" },
    { icon: <FileCheck className="w-5 h-5 text-text-secondary" />, title: "Loan Recommendation" }
  ];

  return (
    <section id="workflow" className="py-24 bg-background-muted border-b border-border">
      <div className="max-w-[1440px] mx-auto px-6 lg:px-12">
        <FadeIn>
          <div className="mb-16">
            <h2 className="text-3xl font-semibold text-text-primary mb-4">Assessment Workflow</h2>
            <p className="text-text-secondary max-w-2xl">A streamlined, secure process designed for enterprise efficiency and transparency.</p>
          </div>
        </FadeIn>
        
        <div className="relative">
          <div className="hidden lg:block absolute top-1/2 left-0 w-full h-[1px] bg-border -translate-y-1/2 z-0"></div>
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 relative z-10">
            {steps.map((step, index) => (
              <FadeIn key={index} delay={index * 0.1}>
                <div className="bg-white border border-border p-6 rounded-card shadow-card flex flex-col items-center text-center relative group">
                  <div className="w-10 h-10 rounded-full bg-background flex items-center justify-center border border-border mb-4">
                    <span className="text-xs font-semibold text-text-secondary">{index + 1}</span>
                  </div>
                  <div className="mb-3">
                    {step.icon}
                  </div>
                  <h4 className="text-sm font-semibold text-text-primary">{step.title}</h4>
                  {index < steps.length - 1 && (
                    <div className="lg:hidden mt-6 text-border flex justify-center">
                      <ChevronRight className="w-6 h-6 rotate-90" />
                    </div>
                  )}
                </div>
              </FadeIn>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

const Footer = () => (
  <footer className="bg-white pt-16 pb-8">
    <div className="max-w-[1440px] mx-auto px-6 lg:px-12">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12 border-b border-border pb-12">
        <div className="col-span-1 md:col-span-1">
          <div className="flex items-center gap-2 mb-6">
            <div className="w-6 h-6 bg-primary rounded flex items-center justify-center">
              <Activity className="w-4 h-4 text-white" />
            </div>
            <span className="font-semibold text-text-primary">CreditPulse AI</span>
          </div>
          <p className="text-sm text-text-secondary leading-relaxed">
            Enterprise MSME assessment platform powered by advanced analytics.
          </p>
        </div>
        <div>
          <h4 className="font-semibold text-text-primary mb-4 text-sm">Platform</h4>
          <ul className="space-y-3 text-sm text-text-secondary">
            <li><a href="#features" className="hover:text-primary transition-colors">Features</a></li>
            <li><a href="#workflow" className="hover:text-primary transition-colors">How It Works</a></li>
          </ul>
        </div>
      </div>
      <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-text-secondary">
        <p>© 2026 IDBI Bank Ltd. All rights reserved.</p>
        <div className="flex items-center gap-4">
          <span>Security Certified</span>
          <span>•</span>
          <span>ISO 27001</span>
        </div>
      </div>
    </div>
  </footer>
);

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background font-sans text-text-primary selection:bg-primary selection:text-white">
      <Navbar />
      <main>
        <Hero />
        <Features />
        <Workflow />
      </main>
      <Footer />
    </div>
  );
}
