import React from 'react';
import { Link } from 'react-router-dom';
import { Activity, ShieldCheck, Lock } from 'lucide-react';

export function Footer() {
  return (
    <footer className="bg-secondary pt-20 pb-10" aria-labelledby="footer-heading">
      <h2 id="footer-heading" className="sr-only">Footer</h2>
      <div className="max-w-[1440px] mx-auto px-6 lg:px-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-16">
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-8 h-8 bg-primary rounded flex items-center justify-center">
                <Activity className="w-4 h-4 text-white" aria-hidden="true" />
              </div>
              <span className="font-display font-bold text-xl text-white">MSME 360 AI</span>
            </div>
            <p className="text-gray-400 leading-relaxed max-w-sm">
              The intelligent underwriting layer for modern financial institutions. Scaling MSME credit safely.
            </p>
          </div>
          <div>
            <h3 className="font-semibold text-white mb-6 text-sm uppercase tracking-wider">Platform</h3>
            <ul className="space-y-4 text-sm text-gray-400">
              <li>
                <a href="#features" className="hover:text-primary-soft transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-soft rounded-sm">Capabilities</a>
              </li>
              <li>
                <a href="#workflow" className="hover:text-primary-soft transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-soft rounded-sm">Workflow</a>
              </li>
              <li>
                <Link to="/login?role=officer" className="hover:text-primary-soft transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-soft rounded-sm">
                  Officer Portal
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-white mb-6 text-sm uppercase tracking-wider">Company</h3>
            <ul className="space-y-4 text-sm text-gray-400">
              <li><a href="#" className="hover:text-primary-soft transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-soft rounded-sm">About</a></li>
              <li><a href="#" className="hover:text-primary-soft transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-soft rounded-sm">Security</a></li>
              <li><a href="#" className="hover:text-primary-soft transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-soft rounded-sm">Contact</a></li>
            </ul>
          </div>
        </div>
        
        <div className="pt-8 border-t border-gray-800 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-gray-500">
          <p>© 2026 IDBI Bank Ltd. All rights reserved.</p>
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <Lock className="w-4 h-4" aria-hidden="true" />
              <span>ISO 27001 Certified</span>
            </div>
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4" aria-hidden="true" />
              <span>Bank-Grade Security</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
