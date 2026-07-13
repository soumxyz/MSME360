import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ShieldCheck, UserCheck, Key, Lock, ArrowRight, Building, HelpCircle } from 'lucide-react';
import { login as apiLogin } from '../lib/api';

export default function Login() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const initialRole = searchParams.get('role') === 'officer' ? 'officer' : 'customer';

  const [activeTab, setActiveTab] = useState<'customer' | 'officer'>(initialRole);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  async function doLogin(u: string, p: string) {
    setIsLoading(true);
    setErrorMessage('');
    try {
      const auth = await apiLogin(u, p);
      // The server, not the UI tab, decides where you land — a customer token
      // never opens the officer console.
      if (auth.role === 'officer') {
        navigate('/officer/dashboard');
      } else {
        navigate('/customer/dashboard');
      }
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      setErrorMessage(msg || 'Sign-in failed. Check your credentials.');
    } finally {
      setIsLoading(false);
    }
  }

  const handleLoginSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) {
      setErrorMessage('Please fill in username and password fields.');
      return;
    }
    void doLogin(username, password);
  };

  const quickDemoLogin = (role: 'customer' | 'officer') => {
    if (role === 'officer') {
      setUsername('officer_demo');
      setPassword('officer123');
      void doLogin('officer_demo', 'officer123');
    } else {
      setUsername('customer_demo');
      setPassword('customer123');
      void doLogin('customer_demo', 'customer123');
    }
  };

  return (
    <div className="min-h-screen grid grid-cols-1 lg:grid-cols-12 bg-background font-sans selection:bg-[#008269] selection:text-white">
      {/* Side Banner: Left Panel */}
      <div className="hidden lg:flex lg:col-span-5 bg-gradient-to-br from-[#005443] to-[#008269] text-white p-12 flex-col justify-between relative overflow-hidden">
        {/* Abstract Graphic Background lines */}
        <div className="absolute inset-0 opacity-10 pointer-events-none">
          <svg className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
            <line x1="0" y1="20%" x2="100%" y2="80%" stroke="white" strokeWidth="2" />
            <line x1="0" y1="50%" x2="100%" y2="50%" stroke="white" strokeWidth="4" />
            <line x1="0" y1="80%" x2="100%" y2="20%" stroke="white" strokeWidth="2" />
          </svg>
        </div>

        <div className="z-10 flex items-center gap-2.5">
          <div className="w-10 h-10 bg-white rounded flex items-center justify-center">
            <ShieldCheck className="w-6 h-6 text-[#008269]" />
          </div>
          <span className="font-bold text-xl tracking-tight">IDBI MSME 360 AI Portal</span>
        </div>

        <div className="z-10 space-y-6 max-w-sm">
          <h1 className="text-3xl font-extrabold leading-tight">
            Institutional-Grade Alternate Data Underwriting
          </h1>
          <p className="text-sm text-white/80 leading-relaxed">
            Integrating GSTN consent pipelines, verified Account Aggregator balances, and EPFO payroll deposits to deliver instant, risk-mitigated credit assessment reports.
          </p>
        </div>

        <div className="z-10 border-t border-white/20 pt-6 text-xs text-white/60">
          © 2026 IDBI Bank Ltd. Subject to RBI alternate credit compliance policies.
        </div>
      </div>

      {/* Main Login Workspace: Right Panel */}
      <div className="lg:col-span-7 flex flex-col justify-center px-6 py-12 md:px-16 lg:px-24 bg-background-muted/40">
        <div className="max-w-md w-full mx-auto space-y-8">
          
          <div className="space-y-2">
            <h2 className="text-2xl font-bold text-text-primary">Sign In to Your Workspace</h2>
            <p className="text-xs text-text-secondary">Enter credentials to authenticate your IDBI banking session.</p>
          </div>

          {/* Unified Tab Switcher */}
          <div className="flex border-b border-border">
            <button
              onClick={() => {
                setActiveTab('customer');
                setErrorMessage('');
              }}
              className={`flex-1 pb-3 text-sm font-semibold border-b-2 transition-all flex items-center justify-center gap-2 ${
                activeTab === 'customer' 
                  ? 'border-[#008269] text-[#008269]' 
                  : 'border-transparent text-text-secondary hover:text-text-primary'
              }`}
            >
              <Building className="w-4 h-4" /> MSME Business Owner
            </button>
            <button
              onClick={() => {
                setActiveTab('officer');
                setErrorMessage('');
              }}
              className={`flex-1 pb-3 text-sm font-semibold border-b-2 transition-all flex items-center justify-center gap-2 ${
                activeTab === 'officer' 
                  ? 'border-[#008269] text-[#008269]' 
                  : 'border-transparent text-text-secondary hover:text-text-primary'
              }`}
            >
              <UserCheck className="w-4 h-4" /> IDBI Credit Officer
            </button>
          </div>

          {/* Error Message banner */}
          {errorMessage && (
            <div className="p-3 bg-error/10 border border-error/20 text-error rounded text-xs font-semibold">
              {errorMessage}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleLoginSubmit} className="space-y-5">
            <div>
              <label className="block text-xs font-bold text-text-primary uppercase tracking-wider mb-2">Username / Login ID</label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary">@</span>
                <input
                  type="text"
                  placeholder={activeTab === 'customer' ? 'Enter business PAN or ID' : 'Enter IDBI Officer username'}
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-9 pr-4 py-2.5 border border-border bg-white rounded text-xs focus:outline-none focus:border-[#008269]"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-text-primary uppercase tracking-wider mb-2">Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-text-secondary absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-9 pr-4 py-2.5 border border-border bg-white rounded text-xs focus:outline-none focus:border-[#008269]"
                />
              </div>
            </div>

            <div className="pt-2">
              {isLoading ? (
                <button
                  type="button"
                  disabled
                  className="w-full py-3 bg-[#008269]/70 text-white font-semibold rounded text-xs flex items-center justify-center gap-2"
                >
                  <Loader2 className="w-4 h-4 animate-spin" /> Verifying Credentials...
                </button>
              ) : (
                <button
                  type="submit"
                  className="w-full py-3 bg-[#008269] hover:bg-[#005443] text-white font-bold rounded text-xs transition-colors flex items-center justify-center gap-1.5 shadow-sm"
                >
                  Sign In <ArrowRight className="w-4 h-4" />
                </button>
              )}
            </div>
          </form>

          {/* Quick Demo Login Help Actions */}
          <div className="border-t border-border pt-6 space-y-3">
            <h3 className="text-xs font-bold text-text-primary flex items-center gap-1.5">
              <HelpCircle className="w-4 h-4 text-[#008269]" /> Quick Demo Logins:
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[10px] font-semibold">
              <button
                onClick={() => quickDemoLogin('customer')}
                className="p-2 border border-border hover:border-[#008269]/40 bg-white rounded transition-colors text-left truncate flex items-center justify-between"
              >
                <span>customer_demo</span>
                <span className="text-[#008269]">Login ➔</span>
              </button>
              <button
                onClick={() => quickDemoLogin('officer')}
                className="p-2 border border-border hover:border-[#008269]/40 bg-white rounded transition-colors text-left truncate flex items-center justify-between"
              >
                <span>officer_demo</span>
                <span className="text-[#008269]">Login ➔</span>
              </button>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}

// Simple inline loader icon
const Loader2 = ({ className }: { className?: string }) => (
  <svg className={`animate-spin ${className}`} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
  </svg>
);
