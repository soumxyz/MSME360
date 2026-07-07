import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeft, Building2, Calendar, FileText, IndianRupee, PieChart, 
  TrendingUp, CheckCircle2, ShieldAlert, FileStack, ShieldCheck, 
  AlertTriangle, Eye, Send, FileSignature, BrainCircuit, Activity,
  Clock, CheckSquare, ChevronDown, ListFilter, Play
} from 'lucide-react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip 
} from 'recharts';

const financialData = [
  { month: 'Jan', revenue: 45, cashflow: 38 },
  { month: 'Feb', revenue: 52, cashflow: 41 },
  { month: 'Mar', revenue: 48, cashflow: 43 },
  { month: 'Apr', revenue: 61, cashflow: 45 },
  { month: 'May', revenue: 55, cashflow: 42 },
  { month: 'Jun', revenue: 67, cashflow: 48 },
];

const applications = [
  { id: 'APP-10294', name: 'ABC Manufacturing', type: 'Manufacturing', status: 'Pending Review', risk: 'Medium', loan: '₹20,00,000' },
  { id: 'APP-10295', name: 'XYZ Traders', type: 'Retail & Commerce', status: 'High Risk', risk: 'High', loan: '₹15,00,000' },
  { id: 'APP-10296', name: 'Sharma Electronics', type: 'Electronics Dealership', status: 'Approved', risk: 'Low', loan: '₹35,00,000' },
  { id: 'APP-10297', name: 'Kumar Textiles', type: 'Apparel Mfg', status: 'Pending Review', risk: 'Medium', loan: '₹25,00,000' },
];

export default function UnderwritingDetails() {
  const { id } = useParams();
  const [selectedApp, setSelectedApp] = useState(
    applications.find(a => a.id === id) || applications[0]
  );
  
  // Real-time assessment report state
  const [realReport, setRealReport] = useState<any>(null);

  // Interactive Chat State
  const [messages, setMessages] = useState([
    {
      sender: 'copilot',
      text: `Hi, I am your CreditPilot AI Copilot. I have synthesized the assessments from Agent 1 (Financial Intelligence) and Agent 2 (Risk & Compliance) for ${selectedApp.name}. Ask me anything about this application!`
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [creditMemo, setCreditMemo] = useState<any>(null);

  // Load real-time assessment report if available in database/localStorage
  React.useEffect(() => {
    const stored = localStorage.getItem('assessment_report');
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setRealReport(parsed);
        
        // Update first copilot message with the real Gemini explanation narrative!
        setMessages([
          {
            sender: 'copilot',
            text: parsed.explanation || `Hi, I am your CreditPilot AI Copilot. I have synthesized the assessments from Agent 1 and Agent 2 for ${selectedApp.name}.`
          }
        ]);
      } catch (err) {
        console.error("Failed to parse local storage report", err);
      }
    }
  }, [selectedApp]);

  // Evidence Panel State
  const [activeEvidenceTab, setActiveEvidenceTab] = useState<string | null>(null);

  // Risk Alert Explanation State
  const [activeAlert, setActiveAlert] = useState<string | null>(null);

  // Human Action Notes
  const [notes, setNotes] = useState('');

  // Audit Logs Timeline State
  const [auditLogs, setAuditLogs] = useState([
    { time: '10:31 AM', event: 'Agent 1 (Financial Analyst) completed pipeline extraction & features normalization.' },
    { time: '10:31 AM', event: 'Agent 2 (Risk Officer) executed GST, AA, and EPFO RBI checks.' },
    { time: '10:32 AM', event: 'Agent 2 flagged: Seasonal Revenue drop during Quarter 2.' },
    { time: '10:33 AM', event: 'Agent 3 (AI Credit Copilot) formulated lending recommendation memo.' }
  ]);

  const handleAppSelect = (app: any) => {
    setSelectedApp(app);
    setCreditMemo(null);
    setActiveEvidenceTab(null);
    setActiveAlert(null);
    setMessages([
      {
        sender: 'copilot',
        text: `Hi, I am your CreditPilot AI Copilot. I have synthesized the assessments from Agent 1 (Financial Intelligence) and Agent 2 (Risk & Compliance) for ${app.name}. Ask me anything about this application!`
      }
    ]);
  };

  const handleSendMessage = (text: string) => {
    if (!text.trim()) return;
    
    const userMsg = { sender: 'user', text };
    setMessages(prev => [...prev, userMsg]);
    setInputText('');

    setTimeout(() => {
      let reply = "I am processing the data models. Could you specify your question?";
      const lower = text.toLowerCase();
      
      const healthScore = realReport ? Math.round(realReport.financial_health_score) : 89;
      const riskVal = realReport ? realReport.risk_category : selectedApp.risk;
      const recommendation = realReport ? realReport.recommendation : 'Approve';
      const explanation = realReport ? realReport.explanation : 'Consistent sales turnover, stable working capital cycles, moderate debt serviceability.';

      if (lower.includes('memo') || lower.includes('generate')) {
        setCreditMemo({
          borrower: selectedApp.name,
          score: healthScore,
          risk: riskVal,
          recommendation: recommendation,
          amount: recommendation === 'REJECT' ? '₹0' : '₹18,50,000',
          reason: explanation,
          preparedBy: 'CreditPilot AI'
        });
        reply = "I have compiled and generated the Credit Memo Note below for your approval.";
      } else if (lower.includes('why') || lower.includes('low risk') || lower.includes('risk')) {
        reply = `The applicant has a risk level of ${riskVal} with a score of ${healthScore}/100. ${explanation}`;
      } else if (lower.includes('summarize') || lower.includes('summary')) {
        reply = `Application summary for ${selectedApp.name}: ${explanation} Recommended Action is ${recommendation}.`;
      } else if (lower.includes('agent 1') || lower.includes('financial')) {
        reply = `Agent 1 reports a financial health score of ${healthScore}/100 with healthy sales turnover.`;
      } else if (lower.includes('agent 2') || lower.includes('compliance')) {
        reply = `Agent 2 evaluated eligibility: ${realReport ? realReport.eligibility : 'Eligible'}. Active policy violations: ${realReport ? realReport.policy_violations.join(', ') || 'None' : 'None'}.`;
      }

      setMessages(prev => [...prev, { sender: 'copilot', text: reply }]);
    }, 1000);
  };

  const handleDecision = (decision: string) => {
    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    setAuditLogs(prev => [
      ...prev,
      { time: timeStr, event: `Credit Officer marked decision as: [${decision.toUpperCase()}]. Notes: "${notes || 'No notes added'}"` }
    ]);
    alert(`Decision saved: ${decision}`);
  };

  return (
    <div className="bg-background-muted min-h-screen">
      {/* Top Header Workspace Label */}
      <div className="bg-white border-b border-border py-4 px-6 lg:px-12 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-primary rounded flex items-center justify-center">
            <Activity className="w-5 h-5 text-white animate-pulse" />
          </div>
          <div>
            <h1 className="font-bold text-lg text-primary tracking-tight">CreditPilot AI Underwriting Workspace</h1>
            <p className="text-[10px] text-text-secondary uppercase tracking-wider font-semibold">Active Session: Senior Loan Officer View</p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs font-semibold bg-success/10 text-success px-3 py-1.5 rounded-full border border-success/20">
          <ShieldCheck className="w-4 h-4" /> AI Assisted Compliance Mode Active
        </div>
      </div>

      <div className="max-w-[1720px] mx-auto grid grid-cols-1 lg:grid-cols-4 gap-6 p-6 lg:p-8">
        
        {/* LEFT SIDEBAR: Application Explorer */}
        <div className="lg:col-span-1 bg-white border border-border rounded-card shadow-sm flex flex-col h-[calc(100vh-140px)]">
          <div className="p-4 border-b border-border">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-bold text-text-primary uppercase tracking-wide flex items-center gap-2">
                <ListFilter className="w-4 h-4" /> Queue Explorer
              </h2>
              <span className="text-xs bg-primary/10 text-primary font-semibold px-2 py-0.5 rounded-full">
                {applications.length} Total
              </span>
            </div>
            <div className="relative">
              <Search className="w-4 h-4 text-text-secondary absolute left-3 top-1/2 -translate-y-1/2" />
              <input 
                type="text" 
                placeholder="Search queue..." 
                className="w-full pl-9 pr-4 py-2 border border-border rounded text-xs focus:outline-none focus:border-primary bg-background-muted/40"
              />
            </div>
          </div>
          
          <div className="flex-grow overflow-y-auto p-4 space-y-3">
            {applications.map((app) => {
              const isActive = app.id === selectedApp.id;
              return (
                <div 
                  key={app.id}
                  onClick={() => handleAppSelect(app)}
                  className={`p-3.5 border rounded-card cursor-pointer transition-all flex items-start justify-between ${
                    isActive 
                      ? 'border-primary bg-primary/5 shadow-sm' 
                      : 'border-border bg-white hover:border-primary/20 hover:bg-background-muted/20'
                  }`}
                >
                  <div className="space-y-1">
                    <h3 className="text-xs font-bold text-text-primary">{app.name}</h3>
                    <p className="text-[10px] text-text-secondary">{app.type} • {app.loan}</p>
                    <div className="pt-2 flex gap-1.5">
                      <span className={`px-2 py-0.5 rounded-[4px] text-[9px] font-semibold ${
                        app.risk === 'Low' ? 'bg-success/10 text-success' : app.risk === 'Medium' ? 'bg-warning/10 text-warning' : 'bg-error/10 text-error'
                      }`}>
                        {app.risk} Risk
                      </span>
                    </div>
                  </div>
                  <span className="text-[9px] font-medium text-text-secondary">{app.id}</span>
                </div>
              );
            })}
          </div>

          <div className="p-4 border-t border-border bg-background-muted/30">
            <div className="grid grid-cols-2 gap-2 text-center text-[10px] font-semibold text-text-secondary">
              <div className="p-2 border border-border rounded bg-white">
                <p className="text-text-primary font-bold">12</p>
                <p>Pending Review</p>
              </div>
              <div className="p-2 border border-border rounded bg-white">
                <p className="text-error font-bold">3</p>
                <p>High Risk</p>
              </div>
            </div>
            <Link to="/" className="mt-4 w-full py-2 bg-white border border-border hover:bg-background text-text-primary text-xs font-medium rounded transition-colors flex items-center justify-center gap-2">
              <ArrowLeft className="w-3.5 h-3.5" /> Return to Main Landing
            </Link>
          </div>
        </div>

        {/* CENTER WORKSPACE: Active Underwriting Details */}
        <div className="lg:col-span-2 space-y-6 overflow-y-auto h-[calc(100vh-140px)] pr-2">
          
          {/* Section 1: Summary Banner */}
          <div className="bg-white border border-border rounded-card p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 bg-primary/10 text-primary border border-primary/20 rounded-card flex items-center justify-center">
                <Building2 className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-text-primary flex items-center gap-2">
                  {selectedApp.name} <span className="text-xs text-text-secondary font-medium">({selectedApp.id})</span>
                </h2>
                <div className="flex flex-wrap gap-x-4 gap-y-1 mt-1 text-xs text-text-secondary">
                  <span>Sector: <strong>{selectedApp.type}</strong></span>
                  <span>Requested Amount: <strong>{selectedApp.loan}</strong></span>
                  <span>Status: <strong className="text-warning">Under AI Review</strong></span>
                </div>
              </div>
            </div>
          </div>

          {/* Section 2: AI Workflow Timeline */}
          <div className="bg-white border border-border rounded-card p-5 shadow-sm">
            <h3 className="text-xs font-bold text-text-primary uppercase tracking-wide mb-4 flex items-center gap-2">
              <Clock className="w-4 h-4 text-primary" /> Credit Assessment Workflow Status
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-3 border border-success/30 bg-success/5 rounded flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold text-success flex items-center gap-1">✓ Agent 1 Completed</p>
                  <p className="text-[10px] text-text-secondary">Financial Intelligence Analyst</p>
                </div>
              </div>
              <div className="p-3 border border-success/30 bg-success/5 rounded flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold text-success flex items-center gap-1">✓ Agent 2 Completed</p>
                  <p className="text-[10px] text-text-secondary">Risk & Compliance Officer</p>
                </div>
              </div>
              <div className="p-3 border border-primary/30 bg-primary/5 rounded flex items-center justify-between animate-pulse">
                <div>
                  <p className="text-xs font-bold text-primary flex items-center gap-1">⚡ Agent 3 Synthesizing</p>
                  <p className="text-[10px] text-text-secondary">AI Credit Copilot Ready</p>
                </div>
              </div>
            </div>
          </div>

          {/* Section 3: Core Indicators */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="bg-white border border-border rounded-card p-4 text-center shadow-sm">
              <p className="text-[9px] uppercase tracking-wider font-bold text-text-secondary mb-1">Health Score</p>
              <p className="text-2xl font-black text-success">
                {realReport ? Math.round(realReport.financial_health_score) : 89}
                <span className="text-xs text-text-secondary">/100</span>
              </p>
            </div>
            <div className="bg-white border border-border rounded-card p-4 text-center shadow-sm">
              <p className="text-[9px] uppercase tracking-wider font-bold text-text-secondary mb-1">AI Risk Band</p>
              <p className="text-2xl font-black text-warning">
                {realReport ? realReport.risk_category : selectedApp.risk}
              </p>
            </div>
            <div className="bg-white border border-border rounded-card p-4 text-center shadow-sm">
              <p className="text-[9px] uppercase tracking-wider font-bold text-text-secondary mb-1">AI Confidence</p>
              <p className="text-2xl font-black text-primary">
                {realReport ? Math.round(realReport.confidence_level) : 94}%
              </p>
            </div>
            <div className="bg-white border border-border rounded-card p-4 text-center shadow-sm">
              <p className="text-[9px] uppercase tracking-wider font-bold text-text-secondary mb-1">Limit Recommendation</p>
              <p className="text-xl font-black text-text-primary">
                {realReport ? (realReport.recommendation === 'REJECT' ? '₹0' : '₹18.5L') : '₹18.5L'}
              </p>
            </div>
            <div className="bg-white border border-border rounded-card p-4 text-center shadow-sm">
              <p className="text-[9px] uppercase tracking-wider font-bold text-text-secondary mb-1">Interest Rate</p>
              <p className="text-xl font-black text-text-primary">
                {realReport 
                  ? (realReport.risk_category === 'LOW' ? '8.5%' : realReport.risk_category === 'MEDIUM' ? '9.3%' : '11.5%') 
                  : '9.3%'
                }
              </p>
            </div>
          </div>

          {/* Section 4: Explainability Checklist */}
          <div className="bg-white border border-border rounded-card p-5 shadow-sm">
            <h3 className="text-xs font-bold text-text-primary uppercase tracking-wide mb-4">Why this Recommendation?</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-medium">
              <div className="space-y-2.5">
                <p className="text-success flex items-center gap-2">✔ GST Revenue increased by 18% YoY</p>
                <p className="text-success flex items-center gap-2">✔ Steady monthly cash balance reserves</p>
                <p className="text-success flex items-center gap-2">✔ High UPI payment transaction velocity</p>
              </div>
              <div className="space-y-2.5">
                <p className="text-success flex items-center gap-2">✔ 100% Payroll deposits (EPFO) stability</p>
                <p className="text-warning flex items-center gap-2">⚠ Seasonal sales dip during quarter 2</p>
                <p className="text-warning flex items-center gap-2">⚠ Pre-existing industrial equipment loan liability</p>
              </div>
            </div>
          </div>

          {/* Section 5: AI Evidence Panel (Interactive) */}
          <div className="bg-white border border-border rounded-card p-5 shadow-sm">
            <h3 className="text-xs font-bold text-text-primary uppercase tracking-wide mb-2">AI Evidence Panel</h3>
            <p className="text-[10px] text-text-secondary mb-4">Click any alternate data source to review transparent raw metrics analyzed by Agent 1 and Agent 2.</p>
            
            <div className="flex flex-wrap gap-2 mb-4">
              {['GST Returns', 'UPI Data', 'Account Aggregator', 'EPFO Records', 'Bank Statements'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveEvidenceTab(activeEvidenceTab === tab ? null : tab)}
                  className={`px-3 py-1.5 rounded-full text-xs font-semibold border transition-all ${
                    activeEvidenceTab === tab
                      ? 'bg-primary text-white border-primary shadow-sm'
                      : 'bg-background-muted/40 hover:bg-background-muted text-text-secondary border-border'
                  }`}
                >
                  {tab} {activeEvidenceTab === tab ? '▴' : '▾'}
                </button>
              ))}
            </div>

            {activeEvidenceTab && (
              <div className="border border-border rounded bg-background-muted/20 p-4 animate-fadeIn text-xs">
                {activeEvidenceTab === 'GST Returns' && (
                  <div>
                    <h4 className="font-bold text-text-primary mb-2">GST Monthly Sales (Self-Reported)</h4>
                    <table className="w-full text-left border-collapse">
                      <thead>
                        <tr className="border-b border-border text-text-secondary font-semibold">
                          <th className="pb-2">Month</th>
                          <th className="pb-2">Sales Amount (INR)</th>
                          <th className="pb-2">Filing Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr className="border-b border-border/50">
                          <td className="py-2">Jan</td>
                          <td className="py-2">₹4.2 Lakhs</td>
                          <td className="py-2 text-success">Filed On Time</td>
                        </tr>
                        <tr className="border-b border-border/50">
                          <td className="py-2">Feb</td>
                          <td className="py-2">₹4.5 Lakhs</td>
                          <td className="py-2 text-success">Filed On Time</td>
                        </tr>
                        <tr>
                          <td className="py-2">Mar</td>
                          <td className="py-2">₹4.8 Lakhs</td>
                          <td className="py-2 text-success">Filed On Time</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                )}

                {activeEvidenceTab === 'UPI Data' && (
                  <div>
                    <h4 className="font-bold text-text-primary mb-2">UPI Merchant Inflow Summaries</h4>
                    <ul className="space-y-1.5">
                      <li>• Average Monthly UPI Credits: <strong>235 credits/month</strong></li>
                      <li>• Unique VPAs Transacting: <strong>142</strong></li>
                      <li>• Digital payment penetration ratio: <strong>92%</strong></li>
                    </ul>
                  </div>
                )}

                {activeEvidenceTab === 'Account Aggregator' && (
                  <div>
                    <h4 className="font-bold text-text-primary mb-2">AA Consent Balance Aggregation</h4>
                    <ul className="space-y-1.5">
                      <li>• Month End Average Balance: <strong>₹45 Lakhs</strong></li>
                      <li>• Non-sufficient Fund (NSF) bounces: <strong>0</strong></li>
                      <li>• Daily Average Thresholds: <strong>Stable (no overdraft triggers)</strong></li>
                    </ul>
                  </div>
                )}

                {activeEvidenceTab === 'EPFO Records' && (
                  <div>
                    <h4 className="font-bold text-text-primary mb-2">EPFO Payroll Deposits</h4>
                    <ul className="space-y-1.5">
                      <li>• Registered Employees: <strong>18 employees</strong></li>
                      <li>• Employee Growth Rate: <strong>+12%</strong></li>
                      <li>• Payroll Deposit Stability: <strong>100% (all deposits completed by 10th of month)</strong></li>
                    </ul>
                  </div>
                )}

                {activeEvidenceTab === 'Bank Statements' && (
                  <div>
                    <h4 className="font-bold text-text-primary mb-2">Extracted Bank Debits & EMIs</h4>
                    <ul className="space-y-1.5">
                      <li>• Total Monthly EMIs: <strong>₹42,000/month</strong></li>
                      <li>• Current Debt-to-Revenue Ratio: <strong>14.5% (well within 35% safe threshold)</strong></li>
                      <li>• Secondary Liabilities: <strong>1 equipment loan (details verified via credit bureau)</strong></li>
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Section 6: Risk Alerts (Interactive) */}
          <div className="bg-white border border-border rounded-card p-5 shadow-sm">
            <h3 className="text-xs font-bold text-text-primary uppercase tracking-wide mb-2">Risk Alerts</h3>
            <p className="text-[10px] text-text-secondary mb-4">Click an alert badge to view the contextual audit mitigation explanation.</p>
            
            <div className="flex flex-wrap gap-3">
              <button 
                onClick={() => setActiveAlert(activeAlert === 'loan' ? null : 'loan')}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-warning/10 text-warning border border-warning/20 text-xs font-semibold"
              >
                <AlertTriangle className="w-3.5 h-3.5" /> Existing Equipment Loan
              </button>
              <button 
                onClick={() => setActiveAlert(activeAlert === 'revenue' ? null : 'revenue')}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-warning/10 text-warning border border-warning/20 text-xs font-semibold"
              >
                <AlertTriangle className="w-3.5 h-3.5" /> Seasonal Revenue Drop
              </button>
              <button 
                onClick={() => setActiveAlert(activeAlert === 'cash' ? null : 'cash')}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-success/10 text-success border border-success/20 text-xs font-semibold"
              >
                <CheckCircle2 className="w-3.5 h-3.5" /> 0 Fraud Triggers Detected
              </button>
            </div>

            {activeAlert && (
              <div className="mt-3 border border-border rounded bg-background-muted/20 p-4 animate-fadeIn text-xs">
                {activeAlert === 'loan' && (
                  <p><strong>Mitigation:</strong> Equipment loan EMI is ₹42,000. Borrower has sufficient debt serviceability coverage (DSCR $1.85$) which supports the new proposed Working Capital limit without defaulting.</p>
                )}
                {activeAlert === 'revenue' && (
                  <p><strong>Mitigation:</strong> Q2 sales dropped by 12% due to monsoon-affected logistics. However, Q3 rebounded by 24%, showing seasonal pattern rather than terminal decay.</p>
                )}
                {activeAlert === 'cash' && (
                  <p><strong>Mitigation:</strong> Graph cycle circular transactions and fake invoices models returned 0 alerts. Accounts matching active fraud blocklists is clean.</p>
                )}
              </div>
            )}
          </div>

          {/* Section 7: Audit Trail Timeline */}
          <div className="bg-white border border-border rounded-card p-5 shadow-sm">
            <h3 className="text-xs font-bold text-text-primary uppercase tracking-wide mb-4">Underwriting Audit Trail</h3>
            <div className="relative border-l-2 border-border pl-6 ml-2 space-y-6">
              {auditLogs.map((log, index) => (
                <div key={index} className="relative">
                  <div className="absolute -left-[31px] top-0.5 bg-white border-2 border-primary rounded-full p-1 w-3.5 h-3.5 flex items-center justify-center">
                    <div className="w-1.5 h-1.5 bg-primary rounded-full" />
                  </div>
                  <div className="text-xs">
                    <span className="font-bold text-primary">{log.time}</span> — <span className="text-text-secondary">{log.event}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* RIGHT AI PANEL: Interactive Credit Copilot Chat Console */}
        <div className="lg:col-span-1 space-y-6 overflow-y-auto h-[calc(100vh-140px)]">
          
          <div className="bg-white border border-border rounded-card p-5 shadow-card flex flex-col h-[400px]">
            <h3 className="text-xs font-bold text-text-primary uppercase tracking-wide mb-4 border-b border-border pb-2 flex items-center gap-2">
              <BrainCircuit className="w-4 h-4 text-primary animate-pulse" /> Agent 3: AI Credit Copilot
            </h3>
            
            {/* Messages */}
            <div className="flex-grow overflow-y-auto space-y-3 mb-4 pr-1 text-[11px] leading-relaxed">
              {messages.map((msg, index) => (
                <div key={index} className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}>
                  <div className={`p-3 rounded-lg max-w-[90%] ${
                    msg.sender === 'user' 
                      ? 'bg-primary text-white rounded-br-none' 
                      : 'bg-background-muted text-text-primary rounded-bl-none border border-border'
                  }`}>
                    {msg.text}
                  </div>
                </div>
              ))}
            </div>

            {/* Quick Prompts */}
            <div className="flex flex-col gap-1.5 mb-3 text-[10px] font-semibold text-primary">
              <button 
                onClick={() => handleSendMessage("Why isn't this applicant Low Risk?")}
                className="w-full text-left px-3 py-1.5 bg-primary/5 hover:bg-primary/10 border border-primary/20 rounded-full transition-colors truncate"
              >
                Why isn't this Low Risk?
              </button>
              <button 
                onClick={() => handleSendMessage("Summarize application")}
                className="w-full text-left px-3 py-1.5 bg-primary/5 hover:bg-primary/10 border border-primary/20 rounded-full transition-colors truncate"
              >
                Summarize Application
              </button>
              <button 
                onClick={() => handleSendMessage("Generate Credit Memo")}
                className="w-full text-left px-3 py-1.5 bg-primary/5 hover:bg-primary/10 border border-primary/20 rounded-full transition-colors truncate"
              >
                Generate Credit Memo
              </button>
            </div>

            {/* Input Bar */}
            <div className="flex gap-2 pt-2 border-t border-border">
              <input 
                type="text"
                placeholder="Ask Credit Copilot..."
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSendMessage(inputText)}
                className="flex-grow border border-border rounded px-3 py-2 text-xs focus:outline-none focus:border-primary"
              />
              <button 
                onClick={() => handleSendMessage(inputText)}
                className="bg-primary hover:bg-primary-hover text-white p-2 rounded transition-colors flex items-center justify-center"
              >
                <Send className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Generated Credit Memo Box */}
          {creditMemo && (
            <div className="bg-white border border-primary/30 rounded-card p-5 shadow-card animate-fadeIn text-xs">
              <div className="flex items-center justify-between pb-2 border-b border-border mb-3">
                <span className="font-bold text-text-primary uppercase tracking-wider flex items-center gap-1.5">
                  <FileText className="w-4 h-4 text-primary" /> Credit Note Memo
                </span>
                <span className="text-[9px] bg-primary/10 text-primary font-bold px-1.5 py-0.5 rounded">PREPARED BY AI</span>
              </div>
              <div className="space-y-2">
                <p>Borrower: <strong>{creditMemo.borrower}</strong></p>
                <p>Health Score: <strong className="text-success">{creditMemo.score}</strong></p>
                <p>Risk Band: <strong>{creditMemo.risk}</strong></p>
                <p>Limit Recommendation: <strong>{creditMemo.amount}</strong></p>
                <p>Reason: <span className="text-text-secondary">{creditMemo.reason}</span></p>
              </div>
            </div>
          )}

          {/* OFFICER ACTION PANEL */}
          <div className="bg-white border border-border rounded-card p-5 shadow-card space-y-4">
            <h3 className="text-xs font-bold text-text-primary uppercase tracking-wide border-b border-border pb-2">Officer Decision</h3>
            
            <textarea 
              rows={3}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Enter underwriting review observations..."
              className="w-full border border-border rounded p-3 text-xs focus:outline-none focus:border-primary resize-none"
            />

            <div className="grid grid-cols-2 gap-2 text-xs font-semibold">
              <button 
                onClick={() => handleDecision("Approve")}
                className="py-2 bg-success hover:bg-success/90 text-white rounded transition-colors"
              >
                Approve
              </button>
              <button 
                onClick={() => handleDecision("Reject")}
                className="py-2 bg-error hover:bg-error/90 text-white rounded transition-colors"
              >
                Reject
              </button>
            </div>

            <button 
              onClick={() => handleDecision("Request Additional Documents")}
              className="w-full py-2 border border-border hover:bg-background-muted text-text-primary text-xs font-medium rounded transition-colors"
            >
              Request Additional Documents
            </button>
            <button 
              onClick={() => handleDecision("Escalate to Committee")}
              className="w-full py-2 border border-border hover:bg-background-muted text-text-primary text-xs font-medium rounded transition-colors"
            >
              Escalate to Committee
            </button>
          </div>

        </div>

      </div>
    </div>
  );
}
