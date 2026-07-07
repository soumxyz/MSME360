import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeft, Building2, Calendar, FileText, IndianRupee, PieChart, 
  TrendingUp, CheckCircle2, ShieldAlert, FileStack, ShieldCheck, 
  AlertTriangle, Eye, Send, FileSignature, BrainCircuit
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

const MetricCard = ({ label, value, trend }: any) => (
  <div className="bg-white border border-border rounded p-4">
    <p className="text-xs font-medium text-text-secondary mb-1">{label}</p>
    <p className="text-xl font-bold text-text-primary mb-1">{value}</p>
    {trend && <p className={`text-[10px] font-medium ${trend.includes('+') ? 'text-success' : 'text-error'}`}>{trend} YoY</p>}
  </div>
);

const SignalBadge = ({ severity }: { severity: string }) => {
  if (severity === 'Low') return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-success/10 text-success border border-success/20 uppercase">Low Risk</span>;
  if (severity === 'Medium') return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-warning/10 text-warning border border-warning/20 uppercase">Med Risk</span>;
  return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-error/10 text-error border border-error/20 uppercase">High Risk</span>;
};

export default function UnderwritingDetails() {
  const { id } = useParams();
  const [notes, setNotes] = useState('');
  const [messages, setMessages] = useState([
    {
      sender: 'copilot',
      text: "Hi, I am your CreditPilot AI Copilot. I have synthesized the assessments from Agent 1 (Financial Intelligence) and Agent 2 (Risk & Compliance). How can I assist you with this application today?"
    }
  ]);
  const [inputText, setInputText] = useState('');

  const handleSendMessage = (text: string) => {
    if (!text.trim()) return;
    
    // User message
    const userMsg = { sender: 'user', text };
    setMessages(prev => [...prev, userMsg]);
    setInputText('');

    // Simulate response based on question keywords
    setTimeout(() => {
      let reply = "I'm analyzing the multi-agent outputs. Could you rephrase your question?";
      const lower = text.toLowerCase();
      
      if (lower.includes('recommend') || lower.includes('why') || lower.includes('2.5') || lower.includes('250') || lower.includes('amount')) {
        reply = "GST turnover has grown by 18% YoY, average monthly cash inflow is ₹45 Lakhs, no active fraud indicators were detected, and the DSCR ratio comfortably supports this credit size. Based on these factors, ₹2.5 Cr is a viable recommended limit.";
      } else if (lower.includes('agent 1') || lower.includes('financial') || lower.includes('revenue') || lower.includes('turnover') || lower.includes('growth')) {
        reply = "Agent 1 (Financial Intelligence Agent) evaluated GSTR-1 filings and AA statements, reporting a Financial Health Score of 82/100. Liquidity is strong (Average balance: ₹45 Lakhs) and Digital Adoption is high (92% digital velocity).";
      } else if (lower.includes('agent 2') || lower.includes('risk') || lower.includes('fraud') || lower.includes('policy') || lower.includes('violation')) {
        reply = "Agent 2 (Risk & Compliance Agent) validated eligibility and reports 0 critical policy violations. High-risk fraud checks (circular transaction cycles, tax defaults) all returned negative (no issues).";
      } else if (lower.includes('tenure') || lower.includes('interest') || lower.includes('rate')) {
        reply = "I suggest a Working Capital term of 12 months with a renewal option, and an interest rate range of 9.25% - 10.50% based on the business's low risk profile.";
      }

      setMessages(prev => [...prev, { sender: 'copilot', text: reply }]);
    }, 1000);
  };

  return (
    <div className="p-6 lg:p-8 w-full max-w-[1440px] mx-auto">
      <div className="mb-6">
        <Link to="/officer/applications" className="inline-flex items-center gap-2 text-sm font-medium text-text-secondary hover:text-primary transition-colors mb-4">
          <ArrowLeft className="w-4 h-4" /> Back to Queue
        </Link>
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold text-text-primary mb-1">Underwriting Review: {id || 'APP-10294'}</h1>
            <p className="text-sm text-text-secondary">Comprehensive AI assessment for Acme Industries Pvt Ltd.</p>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium bg-primary/10 text-primary border border-primary/20">
              <BrainCircuit className="w-4 h-4" /> AI Recommended
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        
        {/* Left Content Area */}
        <div className="xl:col-span-2 space-y-8">
          
          {/* Business Info Header */}
          <div className="bg-white border border-border rounded-card p-6 shadow-sm">
            <div className="flex items-start gap-4 mb-6">
              <div className="w-12 h-12 bg-background-muted rounded border border-border flex items-center justify-center">
                <Building2 className="w-6 h-6 text-text-secondary" />
              </div>
              <div className="flex-1">
                <h2 className="text-xl font-bold text-text-primary">Acme Industries Pvt Ltd</h2>
                <div className="flex flex-wrap gap-x-6 gap-y-2 mt-2 text-sm text-text-secondary">
                  <span className="flex items-center gap-1.5"><FileText className="w-4 h-4" /> GSTIN: 22AAAAA0000A1Z5</span>
                  <span className="flex items-center gap-1.5"><FileSignature className="w-4 h-4" /> PAN: ABCDE1234F</span>
                  <span className="flex items-center gap-1.5"><Calendar className="w-4 h-4" /> Vintage: 8 Years</span>
                  <span className="flex items-center gap-1.5"><PieChart className="w-4 h-4" /> Manufacturing</span>
                </div>
              </div>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-6 border-t border-border">
              <MetricCard label="Requested Loan" value="₹2.5 Cr" />
              <MetricCard label="Annual Revenue" value="₹12.4 Cr" trend="+18%" />
              <MetricCard label="Avg Bank Bal" value="₹45 Lakhs" />
              <MetricCard label="Debtor Days" value="65 Days" trend="+12 Days" />
            </div>
          </div>

          {/* Financial Charts */}
          <div className="bg-white border border-border rounded-card p-6 shadow-sm">
            <h3 className="text-base font-semibold text-text-primary mb-6">Financial Trend Analysis (Last 6 Months)</h3>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={financialData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#0F4C81" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#0F4C81" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorCash" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#16A34A" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#16A34A" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                  <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#6B7280' }} dy={10} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#6B7280' }} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #E5E7EB', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }} 
                  />
                  <Area type="monotone" dataKey="revenue" name="Revenue (Lakhs)" stroke="#0F4C81" strokeWidth={2} fillOpacity={1} fill="url(#colorRev)" />
                  <Area type="monotone" dataKey="cashflow" name="Cash Flow (Lakhs)" stroke="#16A34A" strokeWidth={2} fillOpacity={1} fill="url(#colorCash)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Connected Data Sources Check */}
          <div className="bg-white border border-border rounded-card p-6 shadow-sm">
            <h3 className="text-base font-semibold text-text-primary mb-4">Verified Data Sources</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="flex items-center justify-between p-3 border border-border rounded bg-background-muted/30">
                <span className="text-sm font-medium text-text-primary">GST Returns</span>
                <CheckCircle2 className="w-4 h-4 text-success" />
              </div>
              <div className="flex items-center justify-between p-3 border border-border rounded bg-background-muted/30">
                <span className="text-sm font-medium text-text-primary">Bank Statements</span>
                <CheckCircle2 className="w-4 h-4 text-success" />
              </div>
              <div className="flex items-center justify-between p-3 border border-border rounded bg-background-muted/30">
                <span className="text-sm font-medium text-text-primary">UPI/Merchant Data</span>
                <CheckCircle2 className="w-4 h-4 text-success" />
              </div>
              <div className="flex items-center justify-between p-3 border border-border rounded bg-background-muted/30">
                <span className="text-sm font-medium text-text-primary">EPFO Records</span>
                <CheckCircle2 className="w-4 h-4 text-success" />
              </div>
              <div className="flex items-center justify-between p-3 border border-border rounded bg-background-muted/30">
                <span className="text-sm font-medium text-text-primary">ITR Filing</span>
                <CheckCircle2 className="w-4 h-4 text-success" />
              </div>
              <div className="flex items-center justify-between p-3 border border-border rounded bg-background-muted/30">
                <span className="text-sm font-medium text-text-primary">Utility Bills</span>
                <CheckCircle2 className="w-4 h-4 text-success" />
              </div>
            </div>
          </div>

        </div>

        {/* Right Sidebar - AI & Actions */}
        <div className="xl:col-span-1 space-y-6">
          
          {/* AI Underwriting Profile */}
          <div className="bg-white border border-border rounded-card p-6 shadow-card">
            <div className="flex items-center gap-2 mb-4 pb-4 border-b border-border">
              <ShieldCheck className="w-5 h-5 text-primary" />
              <h3 className="text-base font-bold text-text-primary">CreditPilot AI Workspace</h3>
            </div>
            
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="text-center p-4 bg-background-muted rounded">
                <p className="text-[10px] uppercase tracking-wider text-text-secondary font-semibold mb-1">Financial Health</p>
                <p className="text-3xl font-bold text-success">88</p>
              </div>
              <div className="text-center p-4 bg-background-muted rounded">
                <p className="text-[10px] uppercase tracking-wider text-text-secondary font-semibold mb-1">Risk Confidence</p>
                <p className="text-3xl font-bold text-primary">92%</p>
              </div>
            </div>

            <div className="space-y-4 pt-4 border-t border-border">
              <div>
                <p className="text-xs font-bold text-text-primary mb-2 uppercase tracking-wide">Agent 1: Financial Intelligence</p>
                <div className="grid grid-cols-2 gap-2 text-xs text-text-secondary bg-background-muted/30 p-3 rounded">
                  <span>Growth: <strong>+18%</strong></span>
                  <span>Liquidity: <strong>Good</strong></span>
                  <span>Cash Flow: <strong>Stable</strong></span>
                  <span>Capacity: <strong>Strong</strong></span>
                </div>
              </div>

              <div>
                <p className="text-xs font-bold text-text-primary mb-2 uppercase tracking-wide">Agent 2: Risk & Compliance</p>
                <div className="grid grid-cols-2 gap-2 text-xs text-text-secondary bg-background-muted/30 p-3 rounded">
                  <span>Risk Level: <strong>Low</strong></span>
                  <span>Fraud Status: <strong>None</strong></span>
                  <span>Policy Checks: <strong>Eligible</strong></span>
                  <span>Violations: <strong>0</strong></span>
                </div>
              </div>
            </div>
          </div>

          {/* Agent 3: AI Credit Copilot Chat Console */}
          <div className="bg-white border border-border rounded-card p-6 shadow-card flex flex-col h-[400px]">
            <h3 className="text-sm font-bold text-text-primary mb-4 uppercase tracking-wider border-b border-border pb-2 flex items-center gap-2">
              <BrainCircuit className="w-4 h-4 text-primary animate-pulse" /> Agent 3: AI Credit Copilot
            </h3>
            
            {/* Message History */}
            <div className="flex-grow overflow-y-auto space-y-3 mb-4 pr-1 text-xs">
              {messages.map((msg, index) => (
                <div key={index} className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}>
                  <div className={`p-3 rounded-lg max-w-[85%] leading-relaxed ${msg.sender === 'user' ? 'bg-primary text-white rounded-br-none' : 'bg-background-muted text-text-primary rounded-bl-none border border-border'}`}>
                    {msg.text}
                  </div>
                </div>
              ))}
            </div>

            {/* Quick Ask Suggestion Buttons */}
            <div className="flex flex-wrap gap-1.5 mb-3">
              <button 
                onClick={() => handleSendMessage("Why did you recommend ₹2.5 Cr?")}
                className="px-2.5 py-1 bg-primary/5 hover:bg-primary/10 border border-primary/20 text-[10px] font-medium text-primary rounded-full transition-colors text-left"
              >
                Why ₹2.5 Cr?
              </button>
              <button 
                onClick={() => handleSendMessage("What did Agent 1 find?")}
                className="px-2.5 py-1 bg-primary/5 hover:bg-primary/10 border border-primary/20 text-[10px] font-medium text-primary rounded-full transition-colors text-left"
              >
                Agent 1 Findings
              </button>
              <button 
                onClick={() => handleSendMessage("Are there any risk alerts?")}
                className="px-2.5 py-1 bg-primary/5 hover:bg-primary/10 border border-primary/20 text-[10px] font-medium text-primary rounded-full transition-colors text-left"
              >
                Agent 2 Alerts
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

          {/* Officer Action Panel */}
          <div className="bg-white border border-border rounded-card p-6 shadow-card">
            <h3 className="text-sm font-bold text-text-primary mb-4 uppercase tracking-wider border-b border-border pb-2">Officer Decision</h3>
            
            <div className="mb-4">
              <label className="block text-xs font-semibold text-text-secondary mb-2">Internal Underwriting Notes</label>
              <textarea 
                rows={4}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Enter manual review observations..."
                className="w-full border border-border rounded p-3 text-sm focus:outline-none focus:border-primary resize-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-3 mb-4">
              <button className="col-span-1 py-2.5 bg-success hover:bg-success/90 text-white text-sm font-semibold rounded transition-colors flex items-center justify-center gap-2">
                <CheckCircle2 className="w-4 h-4" /> Approve
              </button>
              <button className="col-span-1 py-2.5 bg-error hover:bg-error/90 text-white text-sm font-semibold rounded transition-colors flex items-center justify-center gap-2">
                <ShieldAlert className="w-4 h-4" /> Reject
              </button>
            </div>

            <div className="space-y-3 pt-4 border-t border-border">
              <button className="w-full py-2 bg-white border border-border hover:bg-background-muted text-text-primary text-sm font-medium rounded transition-colors flex items-center justify-center gap-2">
                <FileStack className="w-4 h-4" /> Request Additional Docs
              </button>
              <button className="w-full py-2 bg-white border border-border hover:bg-background-muted text-text-primary text-sm font-medium rounded transition-colors flex items-center justify-center gap-2">
                <Send className="w-4 h-4" /> Escalate to Committee
              </button>
              <Link to="/officer/health-cards" className="w-full py-2 bg-primary/5 border border-primary/20 hover:bg-primary/10 text-primary text-sm font-medium rounded transition-colors flex items-center justify-center gap-2">
                <Activity className="w-4 h-4" /> Generate Health Card
              </Link>
            </div>

          </div>

        </div>

      </div>
    </div>
  );
}
