import React, { useState } from 'react';
import { Settings as SettingsIcon, User, Shield, BrainCircuit, Check, Save } from 'lucide-react';

export default function Settings() {
  const [activeTab, setActiveTab] = useState<'profile' | 'underwriting' | 'dev'>('profile');
  const [isSaved, setIsSaved] = useState(false);

  // Profile states
  const [profile, setProfile] = useState({
    name: 'Rajesh Kumar',
    email: 'rajesh.kumar@idbibank.com',
    role: 'Senior Credit Officer',
    department: 'MSME Lending & Risk'
  });

  // Risk parameters
  const [minScore, setMinScore] = useState(55);
  const [maxExposure, setMaxExposure] = useState(5000000); // 50L
  const [autoApprove, setAutoApprove] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 3000);
  };

  return (
    <div className="p-6 lg:p-8 w-full max-w-[1000px] mx-auto font-sans bg-[#fafafa]">
      
      {/* Header */}
      <div className="mb-6 flex items-center justify-between border-b border-border pb-4">
        <div>
          <h1 className="text-xl font-bold text-text-primary">System Settings</h1>
          <p className="text-xs text-text-secondary mt-1">Configure profile settings, risk thresholds, and credit decision engines.</p>
        </div>
        <div className="w-10 h-10 bg-primary/10 rounded flex items-center justify-center border border-primary/20">
          <SettingsIcon className="w-5 h-5 text-primary" />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        
        {/* Navigation Sidebar */}
        <div className="md:col-span-1 flex flex-col gap-1.5">
          <button
            onClick={() => setActiveTab('profile')}
            className={`flex items-center gap-2.5 px-4 py-2.5 rounded text-xs font-semibold text-left transition-all cursor-pointer ${
              activeTab === 'profile'
                ? 'bg-primary text-white shadow-sm'
                : 'bg-white border border-border text-text-secondary hover:bg-background-muted'
            }`}
          >
            <User className="w-4 h-4" />
            Profile Settings
          </button>
          <button
            onClick={() => setActiveTab('underwriting')}
            className={`flex items-center gap-2.5 px-4 py-2.5 rounded text-xs font-semibold text-left transition-all cursor-pointer ${
              activeTab === 'underwriting'
                ? 'bg-primary text-white shadow-sm'
                : 'bg-white border border-border text-text-secondary hover:bg-background-muted'
            }`}
          >
            <Shield className="w-4 h-4" />
            Underwriting Config
          </button>
          <button
            onClick={() => setActiveTab('dev')}
            className={`flex items-center gap-2.5 px-4 py-2.5 rounded text-xs font-semibold text-left transition-all cursor-pointer ${
              activeTab === 'dev'
                ? 'bg-primary text-white shadow-sm'
                : 'bg-white border border-border text-text-secondary hover:bg-background-muted'
            }`}
          >
            <BrainCircuit className="w-4 h-4" />
            Methodology Guide
          </button>
        </div>

        {/* Content Pane */}
        <div className="md:col-span-3 bg-white border border-border rounded-card p-6 shadow-card">
          {isSaved && (
            <div className="mb-4 p-3 bg-success/15 border border-success/30 rounded text-success text-xs font-semibold flex items-center gap-1.5">
              <Check className="w-4 h-4" /> Changes have been saved successfully.
            </div>
          )}

          {activeTab === 'profile' && (
            <form onSubmit={handleSave} className="space-y-4">
              <h3 className="text-sm font-bold text-text-primary uppercase tracking-wider border-b border-border pb-2 mb-4">User Profile</h3>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-[11px] font-bold text-text-secondary uppercase tracking-wider mb-2">Display Name</label>
                  <input
                    type="text"
                    value={profile.name}
                    onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                    className="w-full border border-border rounded p-2.5 text-xs focus:outline-none focus:border-primary"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-text-secondary uppercase tracking-wider mb-2">Email Address</label>
                  <input
                    type="email"
                    value={profile.email}
                    onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                    className="w-full border border-border rounded p-2.5 text-xs focus:outline-none focus:border-primary"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-text-secondary uppercase tracking-wider mb-2">Designation</label>
                  <input
                    type="text"
                    value={profile.role}
                    disabled
                    className="w-full border border-border bg-background-muted rounded p-2.5 text-xs text-text-secondary cursor-not-allowed"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-text-secondary uppercase tracking-wider mb-2">Department</label>
                  <input
                    type="text"
                    value={profile.department}
                    disabled
                    className="w-full border border-border bg-background-muted rounded p-2.5 text-xs text-text-secondary cursor-not-allowed"
                  />
                </div>
              </div>

              <div className="pt-4 border-t border-border flex justify-end">
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-semibold rounded shadow-sm transition-colors flex items-center gap-1.5 cursor-pointer"
                >
                  <Save className="w-4 h-4" /> Save Profile
                </button>
              </div>
            </form>
          )}

          {activeTab === 'underwriting' && (
            <form onSubmit={handleSave} className="space-y-4">
              <h3 className="text-sm font-bold text-text-primary uppercase tracking-wider border-b border-border pb-2 mb-4">Underwriting Policies</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-[11px] font-bold text-text-secondary uppercase tracking-wider mb-2">
                    Minimum Auto-Decisioning Score ({minScore})
                  </label>
                  <input
                    type="range"
                    min="30"
                    max="80"
                    value={minScore}
                    onChange={(e) => setMinScore(parseInt(e.target.value))}
                    className="w-full h-2 bg-background-muted rounded-lg appearance-none cursor-pointer accent-primary"
                  />
                  <span className="text-[10px] text-text-secondary block mt-1">Applications scoring below this limit will require mandatory manual underwriter override.</span>
                </div>

                <div>
                  <label className="block text-[11px] font-bold text-text-secondary uppercase tracking-wider mb-2">
                    Maximum Single Exposure Threshold (INR)
                  </label>
                  <select
                    value={maxExposure}
                    onChange={(e) => setMaxExposure(parseInt(e.target.value))}
                    className="w-full border border-border rounded p-2.5 text-xs focus:outline-none focus:border-primary bg-white cursor-pointer"
                  >
                    <option value={2500000}>₹25,00,000 (Mudra Limit)</option>
                    <option value={5000000}>₹50,00,000 (SME standard)</option>
                    <option value={10000000}>₹1,00,00,000 (Prime CGTMSE)</option>
                  </select>
                </div>

                <div className="flex items-center gap-2 pt-2">
                  <input
                    type="checkbox"
                    id="autoApprove"
                    checked={autoApprove}
                    onChange={(e) => setAutoApprove(e.target.checked)}
                    className="w-4 h-4 border-border rounded text-primary focus:ring-primary cursor-pointer"
                  />
                  <label htmlFor="autoApprove" className="text-xs font-semibold text-text-primary cursor-pointer select-none">
                    Enable Low-Risk Auto Approval Pipeline
                  </label>
                </div>
              </div>

              <div className="pt-4 border-t border-border flex justify-end">
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-semibold rounded shadow-sm transition-colors flex items-center gap-1.5 cursor-pointer"
                >
                  <Save className="w-4 h-4" /> Save Thresholds
                </button>
              </div>
            </form>
          )}

          {activeTab === 'dev' && (
            <div className="space-y-4">
              <h3 className="text-sm font-bold text-text-primary uppercase tracking-wider border-b border-border pb-2 mb-4">Methodology & Engine Guides</h3>
              
              <div className="p-5 border border-primary/20 bg-primary/5 rounded">
                <h4 className="text-xs font-bold text-primary flex items-center gap-1.5 uppercase tracking-wider mb-2">
                  <BrainCircuit className="w-4 h-4" /> IDBI CreditPilot Agentic AI Methodology
                </h4>
                <p className="text-xs text-text-secondary leading-relaxed mb-4">
                  Every client health score is computed dynamically by our <strong>Agent 2 ML Engine</strong> using an XGBoost model fit on continuous balance sheets and alternate cash flow metrics. Inputs are parsed by the <strong>Agent 1 Compliance Engine</strong> from raw bank statement uploads and cross-verified against GST filing timelines. Local attributions are calculated using SHAP Tree Explainers and fully explained in natural language via the <strong>Agent 3 Generative Credit Copilot</strong>.
                </p>
                <div className="flex flex-wrap gap-4 text-[10px] font-bold text-text-secondary uppercase">
                  <div className="flex items-center gap-1">
                    <div className="w-1.5 h-1.5 rounded-full bg-success" />
                    <span>Agent 1: Parser Engine</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="w-1.5 h-1.5 rounded-full bg-success" />
                    <span>Agent 2: Scoring Engine</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="w-1.5 h-1.5 rounded-full bg-success" />
                    <span>Agent 3: Copilot Interface</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

      </div>

    </div>
  );
}
