import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Activity } from 'lucide-react';

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  
  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav 
      aria-label="Main Navigation"
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled ? 'bg-background/95 backdrop-blur-md border-b border-border py-3 shadow-sm' : 'bg-transparent py-5'
      }`}
    >
      <div className="max-w-[1440px] mx-auto px-6 lg:px-12 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3 rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background p-1 -ml-1 transition-shadow" aria-label="CreditPulse Home">
          <div className="w-9 h-9 bg-primary rounded-lg flex items-center justify-center shadow-card">
            <Activity className="w-5 h-5 text-white" aria-hidden="true" />
          </div>
          <span className="font-display font-bold text-xl text-primary tracking-tight">CreditPulse</span>
        </Link>
        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-text-secondary">
          <a href="#features" className="hover:text-primary transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary rounded-sm">Platform</a>
          <a href="#workflow" className="hover:text-primary transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary rounded-sm">How it Works</a>
        </div>
        <div className="flex items-center gap-4 text-sm font-medium">
          <Link 
            to="/login?role=officer" 
            className="text-text-secondary hover:text-primary transition-colors hidden md:block focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary rounded-sm px-2 py-1"
          >
            Officer Portal
          </Link>
          <Link 
            to="/register" 
            className="bg-primary hover:bg-primary-hover text-white px-5 py-2.5 rounded-card shadow-card transition-all hover:scale-105 active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background"
          >
            Start Assessment
          </Link>
        </div>
      </div>
    </nav>
  );
}
